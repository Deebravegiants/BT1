# [M] Not using safeMath, leading to loss of funds and pression

## Summary
Severity: Medium
Reporter: shtesesamoubiq
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L123
Type: audit-issue

## Details
# Not using safeMath, leading to loss of funds and pression

## Summary
Not using safeMath, leading to loss of funds and pression 
## Vulnerability Detail
In solidity, it is always rounding down the floating numbers. Using 3 time in a row diving to calculate a number without using safeMath library means pression loss.
## Impact
losing funds of the use of incorrect return price.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L123
## Tool used

Manual Review

## Recommendation
Using safeMath library
