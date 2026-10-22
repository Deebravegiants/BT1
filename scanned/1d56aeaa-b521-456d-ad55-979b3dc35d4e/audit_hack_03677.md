# [H] StakingModule.sol#L420 : `removePlugin` should check whether the plugin has any valid claim

## Summary
Severity: High
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420
Type: audit-issue

## Details
# StakingModule.sol#L420 : `removePlugin` should check whether the plugin has any valid claim

## Summary
[removePlugin](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420) function is used to removed any of the plugin. It does not check whether the plugin has valid claims.

## Vulnerability Detail

Plugins are removed from array.. Refer below line of codes.
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429

There are no check whether the plugin address that is going to be removed has any valid claim.

## Impact

If the plugin has any valid claims, that can not be claimed if the plugin address is removed and replaced by new one.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L420-L429

## Tool used

Manual Review

## Recommendation
Check whether the plugin that is going to be removed has any valid claim. If it has, recover it and then remove the plugin.
