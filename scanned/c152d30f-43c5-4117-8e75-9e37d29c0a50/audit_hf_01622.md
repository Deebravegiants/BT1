# [M] A require check is creating a false sense of security

## Summary
Severity: Medium
Contest weight: 0.3669
Dataset id: 8728
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In addCurrencyToList() we have the following check:
```solidity
if (ERC20(token).balanceOf(msg.sender) == ZERO) {
    revert MustBeHolder();
}
```
It creates false sense of security because everybody can create a malicious token or whatever token and buy just 1 token. This will be enough to bypass the check.

## Recommendation
If you truly want to make this work, it got to be with a whitelist for allowed tokens.
