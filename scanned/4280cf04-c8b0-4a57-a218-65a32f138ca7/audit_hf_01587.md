# [H] MJR-9 Incorrect usage of function returned value

## Summary
Severity: High
Contest weight: 0.0087
Dataset id: 8507
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the vault contract’s withdraw function, which is intended to return the number of vault shares that were burned when a user redeems their tokens. Instead, the implementation returns the raw amount of underlying tokens that were transferred to the caller. This mismatch between the documented API contract and the actual return value constitutes an incorrect‑return‑value bug, a class of accounting errors where a function reports a value that does not reflect the operation performed. The root cause is a developer oversight: the function captures and returns the token transfer amount rather than the share amount calculated by the vault’s accounting logic. Because the function still transfers the correct token amount, the error is not immediately visible on the user interface; however, any external contract, script, or off‑chain service that relies on the returned value to update its internal bookkeeping will record an inaccurate share balance. An attacker or a careless developer could exploit this by assuming they received a larger share balance than they actually hold, leading to subsequent operations (such as further withdrawals or voting) being authorized on an inflated balance. The impact includes potential loss of funds, broken accounting invariants, and user confusion where the UI shows a successful withdrawal but the reported share balance remains unchanged or becomes zero. The bug manifests every time the withdraw function is called, affecting all users of the vault and any protocol components that integrate with it. It was discovered during a formal security audit performed by MixBytes, and its subtle nature makes it hard to notice because the token transfer succeeds and no revert occurs; only the return data is wrong, which many callers may ignore. The proper remediation is to modify the withdraw implementation so that it returns the exact number of shares burned, or to remove the return value entirely if it is not required, thereby aligning the function’s observable behavior with its intended specification and restoring correct accounting across the protocol.

## Recommendation
We recommend to change function code.
