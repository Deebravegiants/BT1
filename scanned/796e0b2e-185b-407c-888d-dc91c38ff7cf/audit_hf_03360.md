# [M] ADLU-3 | Two Separate ADL Factors

## Summary
Severity: Medium
Contest weight: 0.0561
Dataset id: 18214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Keys.MAX_PNL_FACTOR is used when checking if the PnL factor for ADL is exceeded instead of Keys.MAX_PNL_FACTOR_FOR_ADL as in AdlHandler.sol line 123. This can lead to ADL being enabled and not going through, or ADL being consistently disabled due to misconﬁguration between the two factors.

## Recommendation
Use the same factor key for the same validation. If the difference is intended for ﬁner and more precise protocol control, document such behavior.
