# [M] Missing zero address validation in `executeTransaction` function

## Summary
Severity: Medium
Reporter: Obedient Mustard Halibut
Source: https://github.com/sherlock-audit/2024-01-olympus-on-chain-governance/blob/main/bophades/src/external/governance/Timelock.sol#L140-L141
Type: audit-issue

## Details
# Missing zero address validation in `executeTransaction` function

krkba
## Summary
## Vulnerability Detail
Missing zero address validation in `target` address.
## Impact
`target` can be set to zero address.
## Code Snippet
https://github.com/sherlock-audit/2024-01-olympus-on-chain-governance/blob/main/bophades/src/external/governance/Timelock.sol#L140-L141
## Tool used

Manual Review

## Recommendation
Validate the input of `target`
