# [M] Name squatting

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-aave-lens
Published: 2022-02-14
Source: https://github.com/code-423n4/2022-02-aave-lens-findings/issues/27
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-aave-lens/blob/aaf6c116345f3647e11a35010f28e3b90e7b4862/contracts/core/LensHub.sol#L142


# Vulnerability details

## Impact
Creating profiles through `LensHub/PublishingLogic.createProfile` does not cost anything and will therefore result in "name squatting".
A whitelisted profile creator will create many handles that are in demand, even if they don't need them, just to flip them for a profit later.
This ruins the experience for many high-profile users that can't get their desired handle.

## Recommended Mitigation Steps
Consider auctioning off handles to the highest bidder or at least taking a fee such that the cost of name squatting is not zero.
