# [M] Hardcoded gas limit for hook in onSlash may cause reverts

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23454
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The onSlash function in the BaseDelegator contract conditionally invokes a hook via a low-level call if a hook address is set:
```solidity
assembly ("memory-safe") {
    pop(call(HOOK_GAS_LIMIT, hook_, 0, add(calldata_, 0x20), mload(calldata_), 0, 0))
}
```
This call uses a hardcoded gas limit (HOOK_GAS_LIMIT), and the function enforces that at least HOOK_RESERVE + HOOK_GAS_LIMIT * 64 / 63 gas is available before proceeding. If this requirement is not met, the function reverts with `BaseDelegator__InsufficientHookGas`.

This rigid gas enforcement introduces a fragility: if the hook's execution requires more gas than allocated by HOOK_GAS_LIMIT, the call may silently fail or the transaction may revert entirely.

Impact: Hooks that require more gas than the hardcoded limit will consistently fail, potentially breaking integrations. As protocol complexity grows, hardcoded gas limits become brittle and may hinder composability or future extensions.

## Recommendation
Consider introducing a mechanism for the hook gas limit to be configured by the contract owner.
