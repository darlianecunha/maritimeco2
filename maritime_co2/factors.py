"""Default parameters for at-berth OPS-avoidable CO2 of LIQUID BULK (tanker) vessels.

Scope: Onshore Power Supply (OPS) avoided emissions at berth. Shore power
replaces the vessel's auxiliary-engine (hotelling) load, so only the AUXILIARY
ENGINE is considered. Boilers are excluded: at a liquid-bulk terminal the boiler
keeps running on fuel for cargo heating and is not replaced by shore power.

From version 0.2.0 the defaults are the published values of the IMO Fourth GHG
Study (2020): auxiliary engine power output at berth from Table 17, by ship type
and size band, and specific fuel consumption from Table 19. These are fleet
reference values, not measurements of a specific vessel; replace them with ship
data when you have it.
"""

# CO2 carbon conversion factors (tonnes CO2 per tonne of fuel).
# Source: IMO Fourth GHG Study 2020 (fuel carbon content, Cf).
CARBON_FACTORS = {
    "HFO": 3.114,
    "MDO": 3.206,
    "MGO": 3.206,
}

# Specific fuel consumption of auxiliary engines (g fuel per kWh), by fuel.
# Source: IMO Fourth GHG Study 2020, Table 19, auxiliary engines built 2001+.
AUX_SFOC = {
    "HFO": 195.0,
    "MDO": 185.0,
    "MGO": 185.0,
}

# Default bunker fuel assumed for the auxiliary engine at berth.
DEFAULT_FUEL = "MDO"

# SFOC of the default fuel. Kept as a name for backwards compatibility.
DEFAULT_SFOC = AUX_SFOC[DEFAULT_FUEL]  # 185 g/kWh

# Table 17 already gives the power output at berth, so no load factor is applied.
DEFAULT_LOAD_FACTOR = 1.0

# Auxiliary engine power output at berth (kW), by ship type and size band.
# Source: IMO Fourth GHG Study 2020, Table 17. Each band is (lower bound, kW);
# a band runs up to the next lower bound, and the last one is open-ended.
# Size is deadweight (dwt) for oil and chemical tankers and cargo capacity in
# cubic metres (cbm) for liquefied gas tankers.
AUX_POWER_AT_BERTH = {
    "oil_tanker": {
        "size_unit": "dwt",
        "bands": [
            (0, 250), (5_000, 375), (10_000, 690), (20_000, 720),
            (60_000, 620), (80_000, 800), (120_000, 2_500), (200_000, 2_500),
        ],
    },
    "chemical_tanker": {
        "size_unit": "dwt",
        "bands": [(0, 110), (5_000, 330), (10_000, 330), (20_000, 790), (40_000, 790)],
    },
    "liquefied_gas_tanker": {
        "size_unit": "cbm",
        "bands": [(0, 240), (50_000, 1_700), (100_000, 2_500), (200_000, 6_750)],
    },
}

SHIP_TYPES = tuple(AUX_POWER_AT_BERTH)
DEFAULT_SHIP_TYPE = "oil_tanker"


def _band_index(size: float, ship_type: str) -> int:
    if ship_type not in AUX_POWER_AT_BERTH:
        raise ValueError(f"Unknown ship_type '{ship_type}'. Options: {list(SHIP_TYPES)}")
    if size < 0:
        raise ValueError("size must be non-negative.")
    bands = AUX_POWER_AT_BERTH[ship_type]["bands"]
    index = 0
    for i, (lower, _kw) in enumerate(bands):
        if size >= lower:
            index = i
    return index


def aux_power_at_berth(size: float, ship_type: str = DEFAULT_SHIP_TYPE) -> float:
    """Auxiliary engine power output at berth (kW), IMO Fourth GHG Study Table 17.

    `size` is deadweight (t) for oil and chemical tankers and cargo capacity
    (cubic metres) for liquefied gas tankers.
    """
    bands = AUX_POWER_AT_BERTH[ship_type]["bands"] if ship_type in AUX_POWER_AT_BERTH else None
    i = _band_index(size, ship_type)
    return float(bands[i][1])


def size_band_label(size: float, ship_type: str = DEFAULT_SHIP_TYPE) -> str:
    """Label of the Table 17 size band, e.g. '20,000-59,999 dwt' or '200,000+ dwt'."""
    i = _band_index(size, ship_type)
    spec = AUX_POWER_AT_BERTH[ship_type]
    bands, unit = spec["bands"], spec["size_unit"]
    lower = bands[i][0]
    if i == len(bands) - 1:
        return f"{lower:,}+ {unit}"
    return f"{lower:,}-{bands[i + 1][0] - 1:,} {unit}"


# Cargo keywords (English and Portuguese) used to suggest a ship type.
_GAS_CARGO = ("LPG", "GLP", "LNG", "GNL")
_CHEMICAL_CARGO = ("CAUSTIC", "SODA", "ETHANOL", "ETANOL", "ALCOHOL", "ALCOOL", "ÁLCOOL", "VEGETABLE", "VEGETA")


def suggest_ship_type(cargo: str) -> str:
    """Suggest a ship type from a cargo description. A suggestion, not a fact.

    LPG/LNG point to a liquefied gas tanker; caustic soda, ethanol and vegetable
    oils to a chemical tanker; anything else returns 'oil_tanker'. Petroleum
    products (diesel, petrol) are carried by both oil tankers and chemical/
    products tankers, so pass the registered ship type whenever you have it.
    """
    text = str(cargo or "").upper()
    if any(k in text for k in _GAS_CARGO):
        return "liquefied_gas_tanker"
    if any(k in text for k in _CHEMICAL_CARGO):
        return "chemical_tanker"
    return DEFAULT_SHIP_TYPE


# --- Legacy (version 0.1.0) -------------------------------------------------
# Illustrative three-band profile used before 0.2.0. Kept so that code passing
# `profile=AUX_PROFILE` still runs; it is no longer the default.
AUX_PROFILE = {
    "small":  {"max_dwt": 20000,        "aux_power_kw": 500,  "load_factor": 0.50},
    "medium": {"max_dwt": 60000,        "aux_power_kw": 1000, "load_factor": 0.50},
    "large":  {"max_dwt": float("inf"), "aux_power_kw": 1500, "load_factor": 0.50},
}


def band_for_dwt(dwt: float) -> str:
    """Legacy: size band key ('small'|'medium'|'large') of the 0.1.0 profile."""
    for band, p in AUX_PROFILE.items():
        if dwt <= p["max_dwt"]:
            return band
    return "large"
