"""Default parameters for at-berth OPS-avoidable CO2 of LIQUID BULK (tanker) vessels.

Scope: Onshore Power Supply (OPS) avoided emissions at berth. Shore power
replaces the vessel's auxiliary-engine (hotelling) load, so only the AUXILIARY
ENGINE is considered. Boilers are excluded: at a liquid-bulk terminal the boiler
keeps running on fuel for cargo heating and is not replaced by shore power.

IMPORTANT: the auxiliary-power and load-factor values below are ILLUSTRATIVE
defaults aligned with the public IMO Fourth GHG Study (2020) method. They are
NOT calibrated to any private dataset and are NOT authoritative for a specific
vessel. Validate against the primary sources and your own data before reporting.
"""

# CO2 carbon conversion factors (tonnes CO2 per tonne of fuel).
# Source: IMO Fourth GHG Study 2020 (fuel carbon content, Cf).
CARBON_FACTORS = {
    "HFO": 3.114,
    "MDO": 3.206,
    "MGO": 3.206,
}

# Specific Fuel Oil Consumption for auxiliary engines (g fuel per kWh).
DEFAULT_SFOC = 215.0  # g/kWh

# Default bunker fuel assumed for the auxiliary engine at berth.
DEFAULT_FUEL = "MDO"

# Illustrative auxiliary-engine profile for liquid bulk by DWT band.
# aux_power_kw: typical auxiliary demand at berth; load_factor: fraction used.
# Boiler is intentionally absent (excluded for OPS).
AUX_PROFILE = {
    "small":  {"max_dwt": 20000,        "aux_power_kw": 500,  "load_factor": 0.50},
    "medium": {"max_dwt": 60000,        "aux_power_kw": 1000, "load_factor": 0.50},
    "large":  {"max_dwt": float("inf"), "aux_power_kw": 1500, "load_factor": 0.50},
}


def band_for_dwt(dwt: float) -> str:
    """Return the size band key ('small'|'medium'|'large') for a given DWT."""
    for band, p in AUX_PROFILE.items():
        if dwt <= p["max_dwt"]:
            return band
    return "large"
