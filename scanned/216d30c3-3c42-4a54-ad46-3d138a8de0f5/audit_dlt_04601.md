# [M] `claimAndExitFor()` can be used by malicious admin with `RECOVERY_ROLE` to steal funds from the users' accounts

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/84
Type: sherlock-finding

## Details
WATCHPUG

medium

# `claimAndExitFor()` can be used by malicious admin with `RECOVERY_ROLE` to steal funds from the users' accounts

## Summary

The admin with `RECOVERY_ROLE` role can steal funds from the users' accounts because they can specify an arbitrary address when calling `claimAndExitFor()`.

## Vulnerability Detail

In `rescueTokens()`, the `RECOVERY_ROLE` is limited to be only allowed to remove the extra amount that isn't staked.

However, `claimAndExitFor()` allows the `RECOVERY_ROLE` to `claim` and `exit` for any user, and send the funds to any address.

## Impact

A malicious or compromised admin with `RECOVERY ROLE` can effectively rug pull all the users.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L441-L459

## Tool used

Manual Review

## Recommendation

Consider only allowing `claimAndExitFor()` to send the funds to the original `account`:

```diff
- function claimAndExitFor(address account, address to, bytes calldata auxData) external onlyRole(RECOVERY_ROLE) whenPaused nonReentrant returns (uint256, uint256) {
+ function claimAndExitFor(address account, bytes calldata auxData) external onlyRole(RECOVERY_ROLE) whenPaused nonReentrant returns (uint256, uint256) {
-    return (_claim(account, to, auxData), _exit(account, to));
+    return (_claim(account, account, auxData), _exit(account, account));
}
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/84_
