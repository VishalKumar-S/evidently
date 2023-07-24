import numpy as np
import pandas as pd
from pydantic import BaseModel

from evidently.pydantic_utils import PolymorphicModel


def smart_assert_equal(actual, expected):
    if (
        isinstance(actual, BaseModel)
        and isinstance(expected, BaseModel)
        and (
            actual.__class__ is expected.__class__
            or (
                isinstance(actual, PolymorphicModel)
                and isinstance(expected, PolymorphicModel)
                and actual.type == expected.type
            )
        )
    ):
        for field in actual.__fields__.values():
            smart_assert_equal(getattr(actual, field.name), getattr(expected, field.name))
        return
    if isinstance(actual, pd.Series):
        pd.testing.assert_series_equal(actual, expected)
        return
    if isinstance(actual, pd.DataFrame):
        pd.testing.assert_frame_equal(actual, expected)
        return
    np.testing.assert_equal(actual, expected)
