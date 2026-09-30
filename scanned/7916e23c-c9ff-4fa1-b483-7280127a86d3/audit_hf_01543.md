# [M] Approval in BaseVault reduces over time

## Summary
Severity: Medium
Contest weight: 0.1358
Dataset id: 8223
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BaseVault stores users allowances as underlying assets allowances. When a user calls, for example, approve(...), it converts the shares amount in the argument to a corresponding asset amount. This approach means that, over time, due to the value of shares increasing over time (yield from providers), the same amount of shares will be worth more assets. Thus, if users approve a certain allowance, and then a few seconds later, another user tries to use this same allowance amount, it should revert, as this shares amount now equals more assets. The BorrowingVault does not have this issue because it never converts between debt and debtShares and the allowance is stored in debt. Thus, if a user approves another user for, let's say, 100 debt, the other user can always spend 100 debt.

## Proof of Concept
no poc/POCFaillingApproval.t.sol#L32/POCFaillingApproval.t.sol#L32

## Recommendation
Instead of converting to the underlying assets, store the allowances in shares. This is how the openzeppelin ERC4626 implementation does it and is more reliable.
