# [H] `removePlugin()` will break the claim function

## Summary
Severity: High
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429
Type: audit-issue

## Details
# `removePlugin()` will break the claim function

## Summary

When the admin `removePlugin()`, the `pluginIndex` will be changed, the original one will not be available. Users have fund in those plugins will lose the fund.

## Vulnerability Detail

After `removePlugin()` the original `pluginIndex` will not be available. The call to `claim()` will fail due to lack of funds.



## Impact

User's fund could be lost or locked.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L234-L241

## Tool used

Manual Review

## Recommendation

Force `claim()` all user's fund before remove any plugin.
