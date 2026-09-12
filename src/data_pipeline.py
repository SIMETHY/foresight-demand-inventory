from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "Processed"


def log(msg: str) -> None:
    print(msg)


def load_data():
    """Load source datasets with the required date columns parsed."""
    sales = pd.read_csv(
        BASE_DIR / "sales_daily.csv",
        parse_dates=["Date"],
    )
    inventory = pd.read_csv(
        BASE_DIR / "inventory_snapshots.csv",
        parse_dates=["Snapshot_Date"],
    )
    sku = pd.read_csv(
        BASE_DIR / "sku_master.csv",
        parse_dates=["Launch_Date"],
    )
    calendar = pd.read_csv(
        BASE_DIR / "calendar.csv",
        parse_dates=["date"],
    )

    return sales, inventory, sku, calendar


def clean_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    """Fill missing calendar labels used by downstream features."""
    calendar = calendar.copy()
    calendar["holiday"] = calendar["holiday"].fillna("None")
    calendar["promotion_event"] = calendar["promotion_event"].fillna("None")
    return calendar


def validate_and_clean(
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    sku: pd.DataFrame,
):
    """Validate business keys and preserve inventory orphan records separately."""

    # Check duplicate business keys.
    dupe_count_sales = sales.duplicated(subset=["Date", "SKU"]).sum()
    dupe_count_inventory = inventory.duplicated(
        subset=["Snapshot_Date", "SKU"]
    ).sum()

    log(
        f"Duplicate keys: sales={dupe_count_sales}, "
        f"inventory={dupe_count_inventory}"
    )

    # The source pipeline keeps the first sales record for duplicate Date+SKU keys.
    if dupe_count_sales:
        sales = sales.drop_duplicates(
            subset=["Date", "SKU"],
            keep="first",
        )

    # Inventory records with SKUs absent from sku_master cannot be enriched.
    sku_ids = set(sku["SKU"])
    sales_ids = set(sales["SKU"])
    inventory_ids = set(inventory["SKU"])

    sales_orphans = sales_ids - sku_ids
    inventory_orphans = inventory_ids - sku_ids

    log(f"Sales SKUs missing from sku_master: {len(sales_orphans)}")
    log(f"Inventory SKUs missing from sku_master: {len(inventory_orphans)}")

    if sales_orphans:
        raise ValueError(
            "Sales contains SKUs that are not present in sku_master: "
            f"{sorted(sales_orphans)}"
        )

    orphan_mask = inventory["SKU"].isin(inventory_orphans)

    inventory_excluded = inventory[orphan_mask].copy()
    inventory_clean = inventory[~orphan_mask].copy()

    return sales, inventory_clean, inventory_excluded, dupe_count_sales, dupe_count_inventory


def build_fact_sales(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    sku: pd.DataFrame,
) -> pd.DataFrame:
    """Create the enriched daily sales fact table."""
    fact_sales = (
        sales
        .merge(calendar, left_on="Date", right_on="date", how="left")
        .merge(sku, on="SKU", how="left")
        .drop(columns=["date"])
    )

    return fact_sales


def build_fact_inventory(
    inventory_clean: pd.DataFrame,
    sku: pd.DataFrame,
) -> pd.DataFrame:
    """Create the enriched inventory fact table."""
    return inventory_clean.merge(sku, on="SKU", how="left")


def validate_outputs(
    fact_sales: pd.DataFrame,
    fact_inventory: pd.DataFrame,
    sku: pd.DataFrame,
) -> None:
    """Run basic integrity checks on the generated fact tables."""

    sales_missing = int(fact_sales.isnull().sum().sum())
    inventory_missing = int(fact_inventory.isnull().sum().sum())

    if sales_missing:
        raise ValueError(
            f"fact_sales contains {sales_missing} missing values."
        )

    if inventory_missing:
        raise ValueError(
            f"fact_inventory contains {inventory_missing} missing values."
        )

    if not fact_sales["SKU"].isin(set(sku["SKU"])).all():
        raise ValueError("fact_sales contains an unknown SKU.")

    if not fact_inventory["SKU"].isin(set(sku["SKU"])).all():
        raise ValueError("fact_inventory contains an unknown SKU.")


def save_outputs(
    fact_sales: pd.DataFrame,
    fact_inventory: pd.DataFrame,
    inventory_excluded: pd.DataFrame,
    sku: pd.DataFrame,
) -> None:
    """Write processed datasets to the Processed directory."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fact_sales.to_csv(
        OUT_DIR / "fact_sales_daily.csv",
        index=False,
    )
    fact_inventory.to_csv(
        OUT_DIR / "fact_inventory.csv",
        index=False,
    )
    inventory_excluded.to_csv(
        OUT_DIR / "excluded_inventory_skus.csv",
        index=False,
    )
    sku.to_csv(
        OUT_DIR / "dim_sku.csv",
        index=False,
    )


def main():
    sales, inventory, sku, calendar = load_data()

    log(
        f"Loaded: sales={sales.shape}, "
        f"inventory={inventory.shape}, "
        f"sku={sku.shape}, "
        f"calendar={calendar.shape}"
    )

    calendar = clean_calendar(calendar)

    (
        sales,
        inventory_clean,
        inventory_excluded,
        dupe_count_sales,
        dupe_count_inventory,
    ) = validate_and_clean(
        sales,
        inventory,
        sku,
    )

    fact_sales = build_fact_sales(
        sales,
        calendar,
        sku,
    )

    fact_inventory = build_fact_inventory(
        inventory_clean,
        sku,
    )

    log(f"fact_sales shape: {fact_sales.shape}")
    log(f"fact_inventory shape: {fact_inventory.shape}")
    log(f"excluded inventory shape: {inventory_excluded.shape}")

    validate_outputs(
        fact_sales,
        fact_inventory,
        sku,
    )

    save_outputs(
        fact_sales,
        fact_inventory,
        inventory_excluded,
        sku,
    )

    log(f"Pipeline complete. Outputs saved to: {OUT_DIR}")
    log(
        f"Final duplicate-key counts: "
        f"sales={dupe_count_sales}, inventory={dupe_count_inventory}"
    )


if __name__ == "__main__":
    main()
