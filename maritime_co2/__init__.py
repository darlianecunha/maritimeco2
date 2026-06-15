"""maritime-co2: open, citable estimator of OPS-avoidable at-berth CO2 for
liquid bulk (tanker) vessels.

Onshore Power Supply (OPS) replaces the auxiliary-engine load at berth, so the
avoided CO2 is the auxiliary-engine emissions only; boilers are excluded.
Implements the public IMO Fourth GHG Study (2020) activity-based method. Does
not include any proprietary calibration.
"""
from .core import auxiliary_emissions, estimate_ops_savings, EmissionResult
from .factors import CARBON_FACTORS, DEFAULT_SFOC, DEFAULT_FUEL, AUX_PROFILE, band_for_dwt

__version__ = "0.1.0"
__all__ = [
    "auxiliary_emissions",
    "estimate_ops_savings",
    "EmissionResult",
    "CARBON_FACTORS",
    "DEFAULT_SFOC",
    "DEFAULT_FUEL",
    "AUX_PROFILE",
    "band_for_dwt",
]
