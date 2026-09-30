# [M] M-06 | Allow Liquidations While Market Is Disabled

## Summary
Severity: Medium
Contest weight: 0.0927
Dataset id: 22111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All state-modifying functions validate that the feature flag PERPS_SYSTEM is enabled before
allowing transactions to proceed. This includes liquidations, which implies that if the feature flag is
disabled, liquidations cannot be processed.
This is undesirable because open positions that become liquidatable while the feature flag is
disabled can lead to significant bad debt in the system.
Additionally, traders should be allowed to close their open positions even while the market is
disabled to avoid liquidations.

## Recommendation
Consider allowing liquidations and the closing of positions while the market is disabled. This could
be achieved with more finely-tuned feature flags that apply to different functions, similar to how the
BFP market operates.
