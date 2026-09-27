# [M] 2step transferOwnership need

## Summary
Severity: Medium
Reporter: vivi
Source: https://github.com/sherlock-audit/2023-04-splits/blob/main/splits-utils/src/OwnableImpl.sol#L45
Type: audit-issue

## Details
# 2step transferOwnership need

## Summary
Owner could mistake in address, when he call transferOwnership
## Vulnerability Detail
Owner could mistake in address, when he call transferOwnership
## Impact
Owner could lost access to file
## Code Snippet
[Implementation file](https://github.com/sherlock-audit/2023-04-splits/blob/main/splits-utils/src/OwnableImpl.sol#L45)
## Tool used

Manual Review

## Recommendation
Use 2-step transferOwnerShip function from open zeppelin
