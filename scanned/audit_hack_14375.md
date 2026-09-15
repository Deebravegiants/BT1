# [M] For loop gas optimization

## Summary
Severity: Medium
Reporter: 0xAleko
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159
Type: audit-issue

## Details
# For loop gas optimization

## Summary
you can use less gas in for loop
line 156
line 202
## Vulnerability Detail

## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202-L205

## Tool used

Manual Review

## Recommendation
use: 
unchecked {
     ++i;
}
