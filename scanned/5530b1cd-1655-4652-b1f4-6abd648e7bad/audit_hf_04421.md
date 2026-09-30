# [H] H-04 | Loops Vault Decay Invalidates Solvency Check

## Summary
Severity: High
Contest weight: 0.1404
Dataset id: 21897
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Loops vault decays the debt of every loop position over time and this decay is reported by the totalDebt, however the totalDebt function does not reduce the total circulating supply corresponding to the decay of the total position collaterals. As a result the decay will invalidate the solvency check and DoS all functionality until funding has been charged.

## Recommendation
Charge funding before completing every action in the system that relies on the solvency check, or consider accounting for the circulating supply that would decrease from the decay in the solvency check.
