# [M] M-40 | getPairAccounting Includes LAV Assets

## Summary
Severity: Medium
Contest weight: 0.0720
Dataset id: 22212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[FraxlendPair.getPairAccounting](https://github.com/peapodsfinance/fraxlend/blob/dc76f7b45b41fa75e175ca1b17dfb37f9d0f5ee2/src/contracts/FraxlendPair.sol#L142) includes the unlent assets from the LAV. External integrations that depend on that function will receive wrong information. For example, if they calculate the value of a single share using the output of that function, their result will be wrong because they account for assets not present in the pair.

## Recommendation
Exclude the LAV assets.
