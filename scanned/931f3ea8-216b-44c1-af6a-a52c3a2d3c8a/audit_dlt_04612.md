# [M] Using `whenNotPaused` modifier on outbound (exit, claim) methods is a potential brick vulnerability

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/26
Type: sherlock-finding

## Details
pashov

medium

# Using `whenNotPaused` modifier on outbound (exit, claim) methods is a potential brick vulnerability

## Summary
`whenNotPaused` modifier should be used only on inbound (stake, deposit) methods as opposed to using it on outbound (exit, claim) methods also. The latter poses a centralisation vulnerability.

## Vulnerability Detail
You should never add `whenNotPaused` modifier to the outbound (exit, claim, withdraw) methods, because if there is a vulnerability in the `withdraw` functionality then the users are pretty much doomed anyway. If you have the modifier though, the admin can pause the contract and renounce ownership (or pauser role) which can end in the contract being bricked and not usable anymore by users.

## Impact
If the vulnerability is exploited then the stakers will lose 100% of their stake and claimable rewards. It requires a malicious or a comrpomised owner, so Medium severity should be appropriate.

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L167
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L190
## Tool used

Manual Review

## Recommendation
Remove `whenNotPaused` from `exit` and `claim` and all of their partial counterparts (methods)
