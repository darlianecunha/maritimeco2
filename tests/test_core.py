import math
import pandas as pd
from maritime_co2 import auxiliary_emissions, estimate_ops_savings, band_for_dwt


def test_auxiliary_known_value():
    # 1000 kW * 0.5 * 10 h = 5000 kWh; fuel = 5000*215/1e6 = 1.075 t
    # CO2 = 1.075 * 3.206 (MDO) = 3.44645 t
    r = auxiliary_emissions(1000, 0.5, 10, fuel="MDO", sfoc=215)
    assert math.isclose(r.energy_kwh, 5000.0)
    assert math.isclose(r.fuel_tonnes, 1.075, rel_tol=1e-9)
    assert math.isclose(r.co2_tonnes, 3.44645, rel_tol=1e-9)


def test_dwt_banding():
    assert band_for_dwt(15000) == "small"
    assert band_for_dwt(45000) == "medium"
    assert band_for_dwt(90000) == "large"


def test_zero_hours():
    assert auxiliary_emissions(1000, 0.5, 0).co2_tonnes == 0.0


def test_invalid_fuel():
    try:
        auxiliary_emissions(1000, 0.5, 10, fuel="COAL")
        assert False
    except ValueError:
        pass


def test_estimate_ops_savings():
    df = pd.DataFrame({"dwt": [15000, 90000], "berth_hours": [10, 20]})
    out = estimate_ops_savings(df)
    assert {"size_band", "aux_power_kw", "co2_avoided_tonnes"} <= set(out.columns)
    assert (out["co2_avoided_tonnes"] > 0).all()
    assert list(out["size_band"]) == ["small", "large"]
