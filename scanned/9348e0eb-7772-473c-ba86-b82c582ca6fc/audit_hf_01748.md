# [H] H-1 stETH liquidity problem

## Summary
Severity: High
Contest weight: 0.1511
Dataset id: 9545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
L2ERC20Bridge mints stETH without minting a corresponding amount of wstETH on L2 L2ERC20ExtendedTokensBridge.sol#L172. This can lead to insolvency issues, affecting users who have bridged wstETH on L2 and wrapped them to stETH. There is a chance (this can be forced by a malicious user without any losses) that the stETH contract on L2 might lack wstETH in its balance. This will require users who wrapped wstETH to stETH on L2 to: • transfer stETH from L2 to L1; • wrap stETH to wstETH on L1; • transfer wstETH from L1 to L2.

## Recommendation
We recommend minting wstETH on L2, locking them on the stETH contract, and subsequently transferring stETH to the user on L2.
