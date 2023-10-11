import pandas as pd
import pytest
from pyspark.sql import SparkSession

from evidently import ColumnMapping
from evidently.base_metric import ColumnName
from evidently.metrics import ColumnDriftMetric
from evidently.metrics import DataDriftTable
from evidently.report import Report
from evidently.spark.engine import SparkEngine
from tests.conftest import smart_assert_equal


@pytest.mark.parametrize(
    "metric,column_mapping",
    [
        (ColumnDriftMetric(column_name=ColumnName.from_any("a")), ColumnMapping(numerical_features=["a", "b"])),
        (
            ColumnDriftMetric(column_name=ColumnName.from_any("a")),
            ColumnMapping(categorical_features=["a", "b"], target_names=[0, 1, 2], target="a"),
        ),
        (
            ColumnDriftMetric(column_name=ColumnName.from_any("a"), stattest="wasserstein"),
            ColumnMapping(numerical_features=["a", "b"]),
        ),
        (
            ColumnDriftMetric(column_name=ColumnName.from_any("a"), stattest="psi"),
            ColumnMapping(numerical_features=["a", "b"]),
        ),
        (
            ColumnDriftMetric(column_name=ColumnName.from_any("a"), stattest="jensenshannon"),
            ColumnMapping(numerical_features=["a", "b"]),
        ),
        (DataDriftTable(), ColumnMapping(numerical_features=["a", "b"])),
    ],
)
def test_column_data_drift(metric, column_mapping):
    from evidently.options.data_drift import DataDriftOptions

    DataDriftOptions.__fields__["nbinsx"].default = 2

    ref_pd = pd.DataFrame({"a": [0, 1, 2], "b": [1, 1, 1]})
    cur_pd = pd.DataFrame({"a": [0, 0, 0], "b": [0, 1, 1]})

    session = SparkSession.builder.getOrCreate()
    ref = session.createDataFrame(ref_pd)
    cur = session.createDataFrame(cur_pd)

    report = Report(metrics=[metric])
    report.run(reference_data=ref_pd, current_data=cur_pd, column_mapping=column_mapping)
    report._inner_suite.raise_for_error()

    res1 = report.as_dict(include_render=True)["metrics"][0]["result"]

    spark_report = Report(metrics=[metric.copy(deep=True)])
    spark_report.run(reference_data=ref, current_data=cur, column_mapping=column_mapping, engine=SparkEngine)
    spark_report._inner_suite.raise_for_error()

    res2 = spark_report.as_dict(include_render=True)["metrics"][0]["result"]
    smart_assert_equal(res2, res1)
