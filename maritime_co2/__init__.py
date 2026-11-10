"""maritime-co2: open, citable estimator of OPS-avoidable at-berth CO2 for
liquid bulk (tanker) vessels.

Onshore Power Supply (OPS) replaces the auxiliary-engine load at berth, so the
avoided CO2 is the auxiliary-engine emissions only; boilers are excluded.
Implements the public IMO Fourth GHG Study (2020) activity-based method with
the study's own reference values (Table 17 power output at berth, Table 19
specific fuel consumption). Does not include any proprietary calibration.
"""
from .core import auxiliary_emissions, estimate_ops_savings, grid_emissions, EmissionResult
from .factors import (
    CARBON_FACTORS,
    AUX_SFOC,
    DEFAULT_SFOC,
    DEFAULT_FUEL,
    DEFAULT_LOAD_FACTOR,
    DEFAULT_SHIP_TYPE,
    SHIP_TYPES,
    AUX_POWER_AT_BERTH,
    AUX_PROFILE,
    aux_power_at_berth,
    size_band_label,
    suggest_ship_type,
    band_for_dwt,
)

__version__ = "0.2.0"
__all__ = [
    "auxiliary_emissions",
    "estimate_ops_savings",
    "grid_emissions",
    "EmissionResult",
    "CARBON_FACTORS",
    "AUX_SFOC",
    "DEFAULT_SFOC",
    "DEFAULT_FUEL",
    "DEFAULT_LOAD_FACTOR",
    "DEFAULT_SHIP_TYPE",
    "SHIP_TYPES",
    "AUX_POWER_AT_BERTH",
    "AUX_PROFILE",
    "aux_power_at_berth",
    "size_band_label",
    "suggest_ship_type",
    "band_for_dwt",
]
