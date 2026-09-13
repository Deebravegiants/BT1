# [M] The remaining ether is not returned to the user

## Summary
Severity: Medium
Reporter: Ambitious Lemonade Chipmunk
Source: https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/core/Allo.sol#L469-L484
Type: audit-issue

## Details
# The remaining ether is not returned to the user
The remaining ether is not returned to the user.

## Vulnerability Detail
Based on the provided code snippet, msg.value might indeed be greater than baseFee + _amount. Therefore, it's advisable to return any excess ether back to the user.

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/core/Allo.sol#L469-L484
## Impact
If a user provides an excess amount of ether when creating a pool, this excess ether is locked in the Allo contract.

## Code Snippet
https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/allo-v2/contracts/core/Allo.sol#L469-L484

## Tool used

Manual Review

## Recommendation
Calculate the excess amount of ether sent by the user and return the surplus ether to the user.
