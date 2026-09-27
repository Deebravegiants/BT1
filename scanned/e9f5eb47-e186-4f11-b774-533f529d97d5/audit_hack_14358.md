# [M] Missed validations on the Price Range

## Summary
Severity: Medium
Reporter: whiteh4t9527
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# Missed validations on the Price Range

## Summary
When `startPrice - endPrice` is less than `(endTime - startTime) / stepSize` (i.e., `totalSteps`), the price would not changed in each *step* during dutch auction.

## Vulnerability Detail
The [`getPriceAt()`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122) function returns the price at current timestamp based on `priceRange`, `endTime`, `startTime`, and `stepSize`. However, when the `priceRange` is less than `totalSteps`, the price would not change in all steps. For example, when `startPrice = 10`, `endPrice = 0`, and `totalSteps = 20`, the price would not drop from `10` to `9` until the third step.

## Impact
The price would not decrease properly in all steps, which violates the assumption of dutch auction.

## Code Snippet
```solidity
    function getPriceAt(uint256 time) public view returns(uint256) {
        // If auction hasn't started yet, return start price
        if(time < startTime) {
            return startPrice;
        }
        // If auction has ended, return end price
        if(time >= endTime) {
            return endPrice;
        }

        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize;
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
        return price;
    }
```

## Tool used

Manual Review

## Recommendation
Check price range in the constructor.
