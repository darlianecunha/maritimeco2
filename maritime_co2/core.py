"""At-berth OPS-avoidable CO2 for liquid bulk (tanker) vessels.

OPS (Onshore Power Supply) avoided emissions are the CO2 the vessel would emit
running its AUXILIARY ENGINE at berth, which shore power replaces. Boilers are
excluded by design (they keep running for cargo heating).

Method (activity-based, IMO Fourth GHG Study 2020):

    energy_kWh  = aux_power_kW * load_factor * berth_hours
    fuel_tonnes = energy_kWh * SFOC(g/kWh) / 1e6
    CO2_tonnes  = fuel_tonnes * Cf      # = OPS-avoidable emissions on board

Optionally, net of the electricity that replaces it:

    grid_CO2_tonnes    = energy_kWh / 1000 * grid_factor (t CO2 per MWh)
    net_avoided_tonnes = CO2_tonnes - grid_CO2_tonnes
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .factors import (
    AUX_SFOC,
    CARBON_FACTORS,
    DEFAULT_FUEL,
    DEFAULT_LOAD_FACTOR,
    DEFAULT_SHIP_TYPE,
    aux_power_at_berth,
    band_for_dwt,
    size_band_label,
)


@dataclass
class EmissionResult:
    energy_kwh: float
    fuel_tonnes: float
    co2_tonnes: float


def auxiliary_emissions(
    power_kw: float,
    load_factor: float,
    hours: float,
    fuel: str = DEFAULT_FUEL,
    sfoc: Optional[float] = None,
) -> EmissionResult:
    """CO2 from the auxiliary engine at berth (the OPS-avoidable emissions).

    `sfoc` defaults to the IMO Fourth GHG Study value for the fuel
    (185 g/kWh for MDO/MGO, 195 g/kWh for HFO).
    """
    if fuel not in CARBON_FACTORS:
        raise ValueError(f"Unknown fuel '{fuel}'. Options: {list(CARBON_FACTORS)}")
    if not 0 <= load_factor <= 1:
        raise ValueError("load_factor must be between 0 and 1.")
    if power_kw < 0 or hours < 0:
        raise ValueError("power_kw and hours must be non-negative.")
    if sfoc is None:
        sfoc = AUX_SFOC[fuel]
    energy_kwh = power_kw * load_factor * hours
    fuel_tonnes = energy_kwh * sfoc / 1e6
    co2_tonnes = fuel_tonnes * CARBON_FACTORS[fuel]
    return EmissionResult(energy_kwh, fuel_tonnes, co2_tonnes)


def grid_emissions(energy_kwh: float, grid_factor: float) -> float:
    """CO2 (t) emitted by the grid to supply `energy_kwh` from shore.

    `grid_factor` is in tonnes CO2 per MWh (numerically equal to kg per kWh).
    Assumes the ship draws the same energy the auxiliary engine would have
    produced; conversion losses are not included.
    """
    if grid_factor < 0:
        raise ValueError("grid_factor must be non-negative.")
    return energy_kwh / 1000.0 * grid_factor


def estimate_ops_savings(
    df: pd.DataFrame,
    dwt_col: str = "dwt",
    hours_col: str = "berth_hours",
    fuel: str = DEFAULT_FUEL,
    sfoc: Optional[float] = None,
    profile: Optional[dict] = None,
    ship_type: str = DEFAULT_SHIP_TYPE,
    ship_type_col: Optional[str] = None,
    grid_factor: Optional[float] = None,
) -> pd.DataFrame:
    """Estimate OPS-avoidable CO2 for a table of liquid-bulk port calls.

    For each call, the auxiliary-engine emissions at berth are computed (boiler
    excluded) with the power output of IMO Fourth GHG Study Table 17 for the
    ship type and size band. The result is the CO2 that Onshore Power Supply
    would avoid on board.

    Parameters
    ----------
    dwt_col : column with the vessel size. Deadweight (t) for oil and chemical
        tankers; cargo capacity (cubic metres) for liquefied gas tankers.
    ship_type : type applied to every call ('oil_tanker', 'chemical_tanker' or
        'liquefied_gas_tanker') when `ship_type_col` is not given.
    ship_type_col : optional column with the ship type of each call.
    grid_factor : optional grid emission factor in t CO2 per MWh. When given,
        adds `grid_co2_tonnes` and `net_avoided_tonnes`.
    profile : legacy 0.1.0 size-band profile (e.g. `AUX_PROFILE`). When given,
        it replaces the Table 17 values and `ship_type` is ignored.

    Adds columns: ship_type, size_band, aux_power_kw, energy_kwh,
    co2_avoided_tonnes (and the two grid columns when `grid_factor` is given).
    """
    out = df.copy()

    def _row(row):
        size = float(row[dwt_col])
        hours = float(row[hours_col])
        if profile is not None:
            band = band_for_dwt(size)
            p = profile[band]
            stype, power, load = "legacy_profile", p["aux_power_kw"], p["load_factor"]
        else:
            stype = str(row[ship_type_col]) if ship_type_col else ship_type
            band = size_band_label(size, stype)
            power, load = aux_power_at_berth(size, stype), DEFAULT_LOAD_FACTOR
        r = auxiliary_emissions(power, load, hours, fuel, sfoc)
        return stype, band, power, r.energy_kwh, r.co2_tonnes

    res = out.apply(_row, axis=1, result_type="expand")
    out["ship_type"] = res[0]
    out["size_band"] = res[1]
    out["aux_power_kw"] = res[2]
    out["energy_kwh"] = res[3]
    out["co2_avoided_tonnes"] = res[4]
    if grid_factor is not None:
        out["grid_co2_tonnes"] = out["energy_kwh"].map(lambda e: grid_emissions(e, grid_factor))
        out["net_avoided_tonnes"] = out["co2_avoided_tonnes"] - out["grid_co2_tonnes"]
    return out
