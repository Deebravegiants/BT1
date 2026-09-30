# [H] H-13 | Flash Mint Manipulates Supply

## Summary
Severity: High
Contest weight: 0.1795
Dataset id: 22171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
WeightedIndex.flashMint() allows anyone to sandwich protocol actions by manipulating totalSupply(). There are a lot of parts in the protocol that depend on totalSupply: • [WeightedIndex.convertToShares()](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/WeightedIndex.sol#L150) • [WeightedIndex.convertToAssets()](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/WeightedIndex.sol#L160) • [ConversionFactorPTKN._calculateCbrWithDen()](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/voting/ConversionFactorPTKN.sol#L29)

## Recommendation
Either change the code that depends on totalSupply or reconsider the existence of the flashMint function.
