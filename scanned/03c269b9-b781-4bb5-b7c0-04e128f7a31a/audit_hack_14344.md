# [M] If totalSteps is greater than priceRange, the price may remain unchanged even if the step changes.

## Summary
Severity: Medium
Reporter: p0wd3r
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# If totalSteps is greater than priceRange, the price may remain unchanged even if the step changes.

## Summary
If `totalSteps` is greater than `priceRange`, the price may remain unchanged even if the step changes.
## Vulnerability Detail

The calculation formula for Price is as follows:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
```solidity
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

Assuming `priceRange` is 10 and `totalSteps` is 100, the price will not change when `currentStep` is between 1-10.

This design contradicts the intention of price changing with each step.
## Impact
Price does not change completely with the variation of steps.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
## Tool used

Manual Review

## Recommendation
Ensure that `priceRange` is greater than `totalSteps`.
