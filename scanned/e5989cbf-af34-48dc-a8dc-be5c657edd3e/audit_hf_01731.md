# [H] MJR-1 Possible incorrect scaledTotalSupply calculation

## Summary
Severity: High
Contest weight: 0.0141
Dataset id: 9446
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect calculation of the scaled total supply in the AStETH contract. The contract stores a variable representing shares as a signed integer. When the share balance becomes negative, the code later casts this signed value to an unsigned uint256 without checking its sign. Because Solidity performs a two's‑complement conversion, a negative number is interpreted as a very large positive integer, causing an overflow. The overflow propagates to the scaledTotalSupply variable, which is used to represent the total amount of stETH that corresponds to the underlying assets. As a result, the reported total supply can be dramatically higher or lower than the actual amount of assets held by the contract. This mis‑calculation can be triggered whenever a user’s share balance drops below zero, for example after a withdrawal that exceeds the recorded share amount due to rounding errors or edge‑case logic. An attacker who can cause a negative share balance can therefore manipulate the scaled total supply, potentially inflating their own share of the pool or causing other users to receive fewer tokens than expected. From a user’s perspective the symptoms may appear as missing or unexpectedly reduced balances, refunds that are zero, or a total supply displayed in the UI that does not match the sum of individual holdings. The issue was discovered during a manual security audit by MixBytes, where the auditors noted the unchecked conversion at line 595 of AStETH.sol. The bug is subtle because the transaction does not revert; the overflow silently corrupts accounting data, making it hard to detect without deep inspection of the supply calculation logic. The class of bug is a signed‑to‑unsigned casting overflow, a common arithmetic error that violates the protocol’s accounting invariants. To remediate the problem the contract should validate that the share value is non‑negative before casting, or use a safe casting library that reverts on negative inputs, thereby ensuring that scaledTotalSupply always reflects the true amount of assets. Proper checks will restore the integrity of the supply accounting and prevent users from experiencing lost or incorrect token balances.

## Recommendation
Before converting a negative number to the uint256 type, you must make it positive.
