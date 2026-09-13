# [H] `plugins[]` is unbounded array that is looped frequently such as when claims are made

## Summary
Severity: High
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L385-L389
Type: audit-issue

## Details
# `plugins[]` is unbounded array that is looped frequently such as when claims are made

## Summary
`plugins[]` are frequently looped in multiple parts of the protocol such as when claims are made. Should the number of plugins added be too large, it would severely affect the functionality of the protocol.

## Vulnerability Detail
A user will not be able to `stake()`, `claim()` or even `exit()` due to the maximum block gas limit in Polygon. The only function that would be callable is `_claimFromIndividualPlugin()`. But note that since this is a private function, it requires users to call `claimFromIndividualPlugin()` themselves to self exit from a single plugin. The protocol can in theory remove some plugins, but this would temporarily cause the loss of assets for users until they are added back. 

## Impact
Severe malfunction in protocol when number of plugins are too high.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L385-L389

## Tool used

Manual Review

## Recommendation
Set an upper bound for number of allowed plugins.
