# [?] fix: reentrant guards (#1107)

## Summary
Severity: Unknown
Chain: EigenLayer
Component: Layr-Labs/eigenlayer-contracts
Published: 2025-02-14
Source: https://github.com/Layr-Labs/eigenlayer-contracts/commit/c748e03e671b3d45ac173e751989fb61f7412b75
Type: security-commit

## Details
fix: reentrant guards (#1107)

**Motivation:**

Concerns about reentrancy in the DelegationManager and interactions of
completed withdrawals which can call untrusted ERC20 transfers

**Modifications:**

Added reentrant guards across external functions

**Result:**

Preventing cross-function reentrancy in the DelegationManager

---------

Co-authored-by: wadealexc <pragma-services@proton.me>
