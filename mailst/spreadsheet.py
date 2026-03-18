import openpyxl
from openpyxl.utils.cell import column_index_from_string

from .main import Recipient


def load_data_from_xlsx(columns, spreadsheet_path, recipient_class=Recipient):
    _check_columns(columns)
    wb = openpyxl.load_workbook(spreadsheet_path, data_only=True)
    ws = wb.active
    recipients = []
    first_line = None
    last_line = None
    for row_index, row in enumerate(ws.iter_rows(values_only=True), start=1):
        recipient = recipient_class()
        skip = False
        # Step 1: fill in the values from the row
        for column in [c for c in columns if c.spreadsheet_column is not None]:
            column_index = column_index_from_string(column.spreadsheet_column) - 1
            cell_value = row[column_index]
            if cell_value is not None:
                if (
                    column.spreadsheet_column_validation_func is None
                    or column.spreadsheet_column_validation_func(cell_value)
                ):
                    recipient.set_column(column, cell_value)
                else:
                    skip = True
            elif column.spreadsheet_column_validation_func is not None:
                skip = True
            if skip:
                break
        if skip:
            if first_line is not None:
                last_line = row_index - 1
            continue
        # Step 2: compute the values of the columns that have a compute_func defined
        for column in [c for c in columns if c.value_computation_func is not None]:
            value = column.value_computation_func(recipient)
            recipient.set_column(column, value)
        recipients.append(recipient)
        if first_line is None:
            first_line = row_index
        elif last_line is not None:
            raise ValueError(
                f"Line {row_index} found valid, but the range was already closed at line {last_line}."
            )
    return recipients


def _check_columns(columns):
    if not columns:
        raise ValueError("No columns defined.")
    # At least one column must have a spreadsheet_validation_func defined
    if not any(
        column.spreadsheet_column_validation_func is not None for column in columns
    ):
        raise ValueError("At least one column must have a validation function defined.")
