# [M] M-04 Unchecked Approve / Should use safeApprove

## Summary
Severity: Medium
Reporter: GalloDaSballo
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L300-L301
Type: audit-issue

## Details
# M-04 Unchecked Approve / Should use safeApprove

## Summary

[Some tokens do not revert on failure](https://github.com/d-xo/weird-erc20#missing-return-values)

Two instances of the code do not use safeApprove, meaning that if the token doesn't revert on failure, funds may be stuck or lost due to reverts.

## Impact

If the approve fails silently, the contracts will stop working

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L300-L301

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L204-L205

## Tool used

Manual Review

## Recommendation

Use `safeApprove` from either OpenZeppelin or Solmate
