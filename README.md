# maritime-co2

> Open, citable Python library to estimate the at-berth CO2 that **Onshore Power Supply (OPS)** would avoid for **liquid bulk (tanker)** vessels, following the IMO Fourth Greenhouse Gas Study (2020) method.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)
[![Live tool](https://img.shields.io/badge/Live-co2--liquid--bulk--calculator-2ea44f)](https://co2-liquid-bulk-calculator.vercel.app)
<!-- After your first GitHub Release, connect the repo to Zenodo and paste the DOI badge here. -->

## What this is

`maritime-co2` estimates the CO2 that Onshore Power Supply (OPS, or cold ironing) would avoid while a liquid bulk vessel is at berth. When a ship connects to shore power, it shuts down its **auxiliary engines**, so the avoided emissions are the auxiliary-engine emissions at berth.

Scope and method are deliberately transparent and standard. The library does not include any proprietary calibration.

## Key modelling choice

> OPS replaces the **auxiliary engine** (hotelling) load only. **Boilers are excluded**: at a liquid-bulk terminal the boiler keeps running on fuel for cargo heating and is not supplied by shore power. This follows standard OPS accounting practice.

## Method

```
energy_kWh  = aux_power_kW × load_factor × berth_hours
fuel_tonnes = energy_kWh × SFOC(g/kWh) / 1e6
CO2_avoided = fuel_tonnes × Cf
```

Carbon conversion factors (Cf) follow the IMO Fourth GHG Study 2020 (MDO/MGO 3.206, HFO 3.114).

> Note: auxiliary-engine power and load factor defaults are illustrative values aligned with the IMO method, not authoritative for a specific vessel and not calibrated to any private dataset. Validate against the primary sources (IMO Fourth GHG Study 2020; IMO MEPC.391(81)) and your own data before reporting.

## Data sample

`data/sample/itaqui_liquid_bulk_2024_sample.csv` contains 100 real liquid bulk port calls at the Port of Itaqui in 2024 (about 10% of the port's annual calls). Columns are operational inputs only (vessel, date, DWT, product, berthing hours). The CO2 figures produced by this library use the generic IMO method, not the author's calibrated methodology.

## Installation

```bash
git clone https://github.com/darlianecunha/maritime-co2
cd maritime-co2
pip install -e .
```

## Quick start

```python
import pandas as pd
from maritime_co2 import estimate_ops_savings

calls = pd.read_csv("data/sample/itaqui_liquid_bulk_2024_sample.csv")
result = estimate_ops_savings(calls)
print(result[["call_id", "dwt", "size_band", "berth_hours", "co2_avoided_tonnes"]].head())
print("Total OPS-avoidable CO2:", round(result["co2_avoided_tonnes"].sum(), 1), "t")
```

## Running the tests

```bash
pip install pytest
pytest
```

## Roadmap

- [x] OPS-avoidable at-berth CO2 for liquid bulk (auxiliary only)
- [ ] Sensitivity analysis over auxiliary power and load factor
- [ ] Cost and payback module for OPS infrastructure
- [ ] Extend to other vessel types

## Citation

If you use this software, please cite it (see `CITATION.cff`).

## License

MIT
