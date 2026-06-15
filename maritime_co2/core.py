"""At-berth OPS-avoidable CO2 for liquid bulk (tanker) vessels.

OPS (Onshore Power Supply) avoided emissions are the CO2 the vessel would emit
running its AUXILIARY ENGINE at berth, which shore power replaces. Boilers are
excluded by design (they keep running for cargo heating).

Method (activity-based, IMO Fourth GHG Study 2020):

    energy_kWh  = aux_power_kW * load_factor * berth_hours
    fuel_tonnes = energy_kWh * SFOC(g/kWh) / 1e6
    CO2_tonnes  = fuel_tonnes * Cf      # = OPS-avoidable emissions
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .factors import (
    CARBON_FACTORS,
    DEFAULT_SFOC,
    DEFAULT_FUEL,
    AUX_PROFILE,
    band_for_dwt,
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
    sfoc: float = DEFAULT_SFOC,
) -> EmissionResult:
    """CO2 from the auxiliary engine at berth (the OPS-avoidable emissions)."""
    if fuel not in CARBON_FACTORS:
        raise ValueError(f"Unknown fuel '{fuel}'. Options: {list(CARBON_FACTORS)}")
    if not 0 <= load_factor <= 1:
        raise ValueError("load_factor must be between 0 and 1.")
    if power_kw < 0 or hours < 0:
        raise ValueError("power_kw and hours must be non-negative.")
    energy_kwh = power_kw * load_factor * hours
    fuel_tonnes = energy_kwh * sfoc / 1e6
    co2_tonnes = fuel_tonnes * CARBON_FACTORS[fuel]
    return EmissionResult(energy_kwh, fuel_tonnes, co2_tonnes)


def estimate_ops_savings(
    df: pd.DataFrame,
    dwt_col: str = "dwt",
    hours_col: str = "berth_hours",
    fuel: str = DEFAULT_FUEL,
    sfoc: float = DEFAULT_SFOC,
    profile: Optional[dict] = None,
) -> pd.DataFrame:
    """Estimate OPS-avoidable CO2 for a table of liquid-bulk port calls.

    For each call, the auxiliary-engine emissions at berth are computed (boiler
    excluded). The result is the CO2 that Onshore Power Supply would avoid.
    Adds columns: size_band, aux_power_kw, energy_kwh, co2_avoided_tonnes.
    """
    profile = profile or AUX_PROFILE
    out = df.copy()

    def _row(row):
        dwt = float(row[dwt_col])
        band = band_for_dwt(dwt)
        p = profile[band]
        r = auxiliary_emissions(p["aux_power_kw"], p["load_factor"], float(row[hours_col]), fuel, sfoc)
        return band, p["aux_power_kw"], r.energy_kwh, r.co2_tonnes

    res = out.apply(_row, axis=1, result_type="expand")
    out["size_band"] = res[0]
    out["aux_power_kw"] = res[1]
    out["energy_kwh"] = res[2]
    out["co2_avoided_tonnes"] = res[3]
    return out
