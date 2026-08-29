# [H] Inflexible Withdrawal Address in `repayAndWithdraw` Function

## Summary
Severity: High
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-22
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/25
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x7c33363077180573c53b6964aa632740ff8b3157f8ba0c837371e817a7a633c9
**Severity:** high

**Description:**
## Vulnerability Description
The vulnerability arises in the `repayAndWithdraw` function, which internally calls `_repayAndWithdraw`. The `msg.sender` is used as both the `vaultHolder` (the user whose debt will be repaid) and the `receiver` (the user who receives the withdrawn collateral). This implementation does not accommodate scenarios where a user's private key might be compromised, and they wish to receive their collateral in a different, secure wallet. As a result, in cases of compromised wallets, users are forced to withdraw collateral to the same potentially insecure address, risking loss of assets.

## Impact
 Users will be unable to redirect their collateral to a secure address, are left vulnerable to losing their assets.

## Recommendation
I recommend implementing an additional parameter in the `repayAndWithdraw` function that allows users to specify a separate `receiver` address for collateral withdrawal.
