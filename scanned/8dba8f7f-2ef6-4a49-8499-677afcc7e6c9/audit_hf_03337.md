# [M] PPU-3 | No Lower Bound On Virtual Inventory Price Impact

## Summary
Severity: Medium
Contest weight: 0.0696
Dataset id: 18188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getPriceImpactUsd function the priceImpactUsdForVirtualInventory is asserted to be <= the thresholdPriceImpactUsd, otherwise the normal priceImpactUsd is used. This however allows the priceImpactUsdForVirtualInventory to negatively impact users without bound. This way malicious actors in other markets are able to grief users using the same priceImpactUsdForVirtualInventory.

## Recommendation
Modify the priceImpactUsdForVirtualInventory > thresholdPriceImpactUsd comparison to priceImpactUsdForVirtualInventory < thresholdPriceImpactUsd.
