# [M] M-01 | Hardcoded GMX Address Can Lead To DoS

## Summary
Severity: Medium
Contest weight: 0.0765
Dataset id: 21974
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GmxUtils contract uses the gExchangeRouter and reader contracts, saving their addresses as constants during deployment. However, it is recommended by GMX to allow these addresses to be changeable (not immutable) and to provide setter functions. These contracts are currently used in essential functions by the protocol, meaning if they were to be changed, the protocol will not function correctly until the addresses are updated through an upgrade.

## Recommendation
Reference GMX's datastore and use the address that is stored there for applicable GMX addresses.
