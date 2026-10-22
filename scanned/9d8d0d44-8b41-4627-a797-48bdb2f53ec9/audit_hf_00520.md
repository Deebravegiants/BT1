# [M] M-11 | Cleared borrowedVEth

## Summary
Severity: Medium
Contest weight: 0.1132
Dataset id: 1978
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a long position is being modified, its borrowedVEth is set to the absolute value of vEthFromZero. In some cases, it's possible to have a small amount of vGasAmount with 0 vEthFromZero due to the traded vETH matching the vEthToZero, primarily when operating with small position sizes and trade prices. This leads to a long position that does not have a loaned amount. This leaves the Foil contract with less available collateral than it should have and in result, the last user will not be able to exit.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/blob/22f09a942e332c3e37c724943ce8f1635cc35e2f/packages/protocol/test/fuzzing/FoundryPlayground.sol#L42

## Recommendation
Validate that any opened long position has positive borrowedVEth: require(borrowedVEth > 0)
