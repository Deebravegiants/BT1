# [M] Intended but missing pausability in `FeeBuyback`

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L39
Type: audit-issue

## Details
# Intended but missing pausability in `FeeBuyback`

## Summary
The docs show an intention of pausability but it is missing in the code

## Vulnerability Detail
In the NatSpec of the `submit` method in `FeeBuyback` we see this comment `* @dev function can be paused` which shows the developers' intent to be able to pause this functionality, but pausability is not present in the code. 

## Impact
This is a case of missing (possibly forgotten) desired functionality which is usually a security measure, so a potential attack won't be stoppable even though the devs intended to have that power. 

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L39
## Tool used

Manual Review

## Recommendation
Make the contract inherit `Pausable` from OpenZeppelin and add `whenNotPaused` modifier to `submit` method
