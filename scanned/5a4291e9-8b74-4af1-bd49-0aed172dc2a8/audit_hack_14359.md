# [M] potential rounding down to zero in currentStep and price calculation

## Summary
Severity: Medium
Reporter: ginlee
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L118
Type: audit-issue

## Details
# potential rounding down to zero in currentStep and price calculation

## Summary
potential rounding down to zero in currentStep and price calculation

## Vulnerability Detail
```solidity
uint256 currentStep = timePassed / stepSize;
```
It is possible that timePassed is less than stepSize in currentStep calculation which will lead to rounding down to zero in solidity

## Impact
Due to currentStep being 0, this will result in
```solidity
 uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```
evaluating to zero, meaning the value of price will be equal to startPrice.Therefore, if timePassed is less than stepSize, the calculated price will be equal to startPrice, and it will not gradually decrease over time as expected. This behavior may deviate from the expected price behavior. It will also affect later calculation in mint function, which may lead to fund loss

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L118
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122

## Tool used
Manual Review

## Recommendation
add check 
```solidity
require(timePassed > stepSize, "currentStep calculation error")
```
