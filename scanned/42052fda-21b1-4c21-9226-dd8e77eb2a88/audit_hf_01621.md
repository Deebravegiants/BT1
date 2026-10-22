# [M] Solmate safeTransfer method does not

## Summary
Severity: Medium
Contest weight: 0.3790
Dataset id: 8727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Solmate safeTransfer methods are used for transferring ERC20 tokens. However, as we can see
```solidity
/// @dev Note that none of the functions in this library check that a token has code at all! That responsibility is delegated to the caller.
```
doesn't have contract in it, it will always return success, bypassing the return value check. Due to this protocol will think that funds has been transferred and successful, and records will be accordingly calculated, but in reality funds were never transferred.

## Recommendation
Use OpenZeppelin's safeERC20 or implement a code existence check.
