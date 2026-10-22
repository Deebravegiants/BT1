# [H] MJR-1 Possible withdraw unavailiability

## Summary
Severity: High
Contest weight: 0.0224
Dataset id: 10257
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an accounting error in the vault contract that manages token deposits and withdrawals. When a user initiates a withdrawal, the contract transfers the requested tokens but fails to update the internal vault state that records the total amount of tokens held. Because the stored balance is not decremented, the contract believes more tokens are still available than actually are. Subsequent withdrawal attempts therefore request an amount that exceeds the real token balance, causing the transaction to revert. This situation can occur after any successful withdrawal and persists until the state is corrected, meaning users may see a positive balance in the UI but are unable to retrieve their funds. The issue was discovered during a manual audit that compared the contract’s external token transfers with its internal accounting variables and noticed the mismatch. It is hard to notice because the contract does not emit explicit error messages about insufficient vault liquidity; instead, the generic revert hides the underlying accounting flaw. The impact is that legitimate users cannot withdraw their assets, effectively locking funds and breaking the expected deposit‑withdraw lifecycle. The bug belongs to the class of state‑management or accounting bugs where internal bookkeeping does not reflect external token movements. To fix the problem, the withdraw function must correctly decrement the vault’s stored balance (or otherwise reconcile the internal accounting) after each successful transfer, ensuring that future withdrawal calculations are based on the actual remaining token pool. Proper checks should be added to prevent withdrawals that would exceed the real token balance, and comprehensive tests should verify that the internal state matches the external token balances after every deposit and withdrawal operation.

## Recommendation
It is recommended to make accounting of deposit/withdraw operation properly
