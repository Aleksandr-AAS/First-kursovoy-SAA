
import pandas as pd
from src.reports import read_xls_file_df


def test_read_xls_file_df_basic(tmp_path):
    """Базовый тест чтения файла"""
    test_file = tmp_path / "test.xls"
    pd.DataFrame({"test": [1]}).to_excel(test_file, index=False)

    result = read_xls_file_df(str(test_file))
    assert isinstance(result, pd.DataFrame)
    assert result["test"].iloc[0] == 1
