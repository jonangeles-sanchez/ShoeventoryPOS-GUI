from pathlib import Path
import pandas as pd
import time


def create_excel_file():
    current_dir = Path(__file__).parent
    current_time_to_display = time.strftime("%Y-%m-%d", time.localtime())
    # check if it exists, if so, use that one
    excel_file = current_dir / f"shoeventory_{current_time_to_display}.xlsx"
    if excel_file.exists():
        df = pd.read_excel(excel_file)
    else:
        df = pd.DataFrame(columns=["id",
                                   "shoeType",
                                   "shoeName",
                                   "shoeColor",
                                   "shoeSize",
                                   "shoeQuantity",
                                   "shoePrice",
                                   "collectionId"])
    return df


def add_shoe_to_excel(shoe):
    df = create_excel_file()
    new_row = pd.DataFrame([shoe])
    df = pd.concat([df, new_row], ignore_index=True)
    current_dir = Path(__file__).parent
    current_time_to_display = time.strftime("%Y-%m-%d", time.localtime())
    excel_file = current_dir / f"shoeventory_{current_time_to_display}.xlsx"
    df.to_excel(excel_file, index=False)
    return df
