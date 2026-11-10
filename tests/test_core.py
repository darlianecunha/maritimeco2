import math

import pandas as pd
import pytest

from maritime_co2 import (
    AUX_PROFILE,
    auxiliary_emissions,
    aux_power_at_berth,
    band_for_dwt,
    estimate_ops_savings,
    grid_emissions,
    size_band_label,
    suggest_ship_type,
)


def test_auxiliary_known_value():
    # 1000 kW * 0.5 * 10 h = 5000 kWh; fuel = 5000*215/1e6 = 1.075 t
    # CO2 = 1.075 * 3.206 (MDO) = 3.44645 t
    r = auxiliary_emissions(1000, 0.5, 10, fuel="MDO", sfoc=215)
    assert math.isclose(r.energy_kwh, 5000.0)
    assert math.isclose(r.fuel_tonnes, 1.075, rel_tol=1e-9)
    assert math.isclose(r.co2_tonnes, 3.44645, rel_tol=1e-9)


def test_default_sfoc_follows_fuel():
    # IMO Fourth GHG Study Table 19: 185 g/kWh for MDO/MGO, 195 g/kWh for HFO
    assert math.isclose(auxiliary_emissions(1000, 1, 10, fuel="MDO").fuel_tonnes, 1.85)
    assert math.isclose(auxiliary_emissions(1000, 1, 10, fuel="MGO").fuel_tonnes, 1.85)
    assert math.isclose(auxiliary_emissions(1000, 1, 10, fuel="HFO").fuel_tonnes, 1.95)


def test_zero_hours():
    assert auxiliary_emissions(1000, 0.5, 0).co2_tonnes == 0.0


def test_invalid_inputs():
    with pytest.raises(ValueError):
        auxiliary_emissions(1000, 0.5, 10, fuel="COAL")
    with pytest.raises(ValueError):
        auxiliary_emissions(1000, 1.5, 10)
    with pytest.raises(ValueError):
        auxiliary_emissions(-1, 0.5, 10)
    with pytest.raises(ValueError):
        aux_power_at_berth(45000, "bulk_carrier")
    with pytest.raises(ValueError):
        aux_power_at_berth(-1)


@pytest.mark.parametrize(
    "size, kw",
    [(0, 250), (4_999, 250), (5_000, 375), (9_999, 375), (10_000, 690), (19_999, 690),
     (20_000, 720), (59_999, 720), (60_000, 620), (79_999, 620), (80_000, 800),
     (119_999, 800), (120_000, 2_500), (199_999, 2_500), (200_000, 2_500), (400_000, 2_500)],
)
def test_oil_tanker_table17(size, kw):
    assert aux_power_at_berth(size) == kw
    assert aux_power_at_berth(size, "oil_tanker") == kw


@pytest.mark.parametrize(
    "size, kw",
    [(0, 110), (4_999, 110), (5_000, 330), (19_999, 330), (20_000, 790), (39_999, 790), (40_000, 790), (150_000, 790)],
)
def test_chemical_tanker_table17(size, kw):
    assert aux_power_at_berth(size, "chemical_tanker") == kw


@pytest.mark.parametrize(
    "cbm, kw",
    [(0, 240), (49_999, 240), (50_000, 1_700), (99_999, 1_700), (100_000, 2_500), (199_999, 2_500), (200_000, 6_750)],
)
def test_gas_tanker_table17(cbm, kw):
    assert aux_power_at_berth(cbm, "liquefied_gas_tanker") == kw


def test_size_band_labels():
    assert size_band_label(45_000) == "20,000-59,999 dwt"
    assert size_band_label(250_000) == "200,000+ dwt"
    assert size_band_label(8_000, "liquefied_gas_tanker") == "0-49,999 cbm"


def test_suggest_ship_type():
    assert suggest_ship_type("ABASTECIMENTO, GLP") == "liquefied_gas_tanker"
    assert suggest_ship_type("LPG") == "liquefied_gas_tanker"
    assert suggest_ship_type("SODA CÁUSTICA") == "chemical_tanker"
    assert suggest_ship_type("Ethanol") == "chemical_tanker"
    assert suggest_ship_type("DIESEL, GASOLINA") == "oil_tanker"
    assert suggest_ship_type("") == "oil_tanker"
    assert suggest_ship_type(None) == "oil_tanker"


def test_reference_call_matches_decarbport():
    # Aframax example of decarbport.com: 105,000 dwt, 36 h, MGO -> 800 kW
    df = pd.DataFrame({"dwt": [105_000], "berth_hours": [36]})
    out = estimate_ops_savings(df, fuel="MGO")
    assert out.loc[0, "aux_power_kw"] == 800
    assert math.isclose(out.loc[0, "energy_kwh"], 28_800.0)
    assert math.isclose(out.loc[0, "co2_avoided_tonnes"], 28_800 * 185 / 1e6 * 3.206, rel_tol=1e-12)
    assert round(out.loc[0, "co2_avoided_tonnes"], 4) == 17.0816


def test_estimate_ops_savings_default_is_oil_tanker():
    df = pd.DataFrame({"dwt": [15_000, 90_000], "berth_hours": [10, 20]})
    out = estimate_ops_savings(df)
    assert {"ship_type", "size_band", "aux_power_kw", "energy_kwh", "co2_avoided_tonnes"} <= set(out.columns)
    assert list(out["ship_type"]) == ["oil_tanker", "oil_tanker"]
    assert list(out["aux_power_kw"]) == [690, 800]
    assert list(out["size_band"]) == ["10,000-19,999 dwt", "80,000-119,999 dwt"]
    assert (out["co2_avoided_tonnes"] > 0).all()


def test_estimate_ops_savings_by_ship_type_column():
    df = pd.DataFrame({
        "dwt": [47_000, 47_000, 8_000],
        "berth_hours": [46.8, 46.8, 24],
        "ship_type": ["oil_tanker", "chemical_tanker", "liquefied_gas_tanker"],
    })
    out = estimate_ops_savings(df, ship_type_col="ship_type")
    assert list(out["aux_power_kw"]) == [720, 790, 240]
    assert [round(v, 4) for v in out["co2_avoided_tonnes"]] == [19.9854, 21.9285, 3.4163]


def test_grid_factor_adds_net_avoided():
    df = pd.DataFrame({"dwt": [45_000], "berth_hours": [30]})
    out = estimate_ops_savings(df, fuel="MGO", grid_factor=0.0461)
    assert math.isclose(out.loc[0, "energy_kwh"], 21_600.0)
    assert math.isclose(out.loc[0, "grid_co2_tonnes"], 21.6 * 0.0461)
    assert math.isclose(out.loc[0, "net_avoided_tonnes"], out.loc[0, "co2_avoided_tonnes"] - 21.6 * 0.0461)
    assert math.isclose(grid_emissions(1000, 0.2), 0.2)
    with pytest.raises(ValueError):
        grid_emissions(1000, -0.1)
    assert "grid_co2_tonnes" not in estimate_ops_savings(df).columns


def test_legacy_profile_still_runs():
    # 0.1.0 behaviour is preserved when the old profile and SFOC are passed explicitly
    assert band_for_dwt(15_000) == "small"
    assert band_for_dwt(45_000) == "medium"
    assert band_for_dwt(90_000) == "large"
    df = pd.DataFrame({"dwt": [15_000, 90_000], "berth_hours": [10, 20]})
    out = estimate_ops_savings(df, profile=AUX_PROFILE, sfoc=215)
    assert list(out["size_band"]) == ["small", "large"]
    assert math.isclose(out.loc[0, "co2_avoided_tonnes"], 500 * 0.5 * 10 * 215 / 1e6 * 3.206)
    assert math.isclose(out.loc[1, "co2_avoided_tonnes"], 1500 * 0.5 * 20 * 215 / 1e6 * 3.206)
