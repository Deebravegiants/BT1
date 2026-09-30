# [M] M-07 | Callback Gas Is Never Specified

## Summary
Severity: Medium
Contest weight: 0.0955
Dataset id: 1991
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _updateOwnership function concludes with a callback to the shadow NFT via _shadow.executeCallback(guid);. While this callback is included in the gas cost, it adds only a negligible increase of 20k gas: uint128 baseGasCost = withCallback _BASE_OWNERSHIP_UPDATE_COST_WITH_CALLBACK // 100k _BASE_OWNERSHIP_UPDATE_COST; // 80k This small gas amount is insufficient to cover any callback, especially a more complex one. Additionally, the callback has no predefined gas limit, which means it could unintentionally consume more gas than expected, causing the function to revert with an OOG error.

## Recommendation
Consider passing the gas limit as a parameter and enforcing it during the callback execution.
