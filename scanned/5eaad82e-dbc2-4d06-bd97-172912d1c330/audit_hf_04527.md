# [H] H-07 | Minimum Delegate Time Not Set

## Summary
Severity: High
Contest weight: 0.1429
Dataset id: 22091
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The core system has setMarketMinDelegateTime() function which has to be called by integrating
markets to set their minimum waiting time for the LPs to withdraw their collateral after they have
delegated it.
The PerpsMarket doesn't call this function which lets LPs delegate and undelegate collateral in the
same block.
This can lead to some unexpected behaviors such as interest rate manipulation or risk-free yield
opportunity by sandwiching a settlement to gain from fees by depositing a large amount of collateral
and the withdrawing it.

## Recommendation
Set some minimum delegate time.
