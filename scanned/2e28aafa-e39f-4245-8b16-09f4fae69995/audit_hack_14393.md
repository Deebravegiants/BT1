# [H] The lack of input validation on constructor function parameters can result in the NFT price not changing.

## Summary
Severity: High
Reporter: ziyou-
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# The lack of input validation on constructor function parameters can result in the NFT price not changing.

## Summary
The lack of input validation on constructor function parameters can result in the NFT price not changing.

## Vulnerability Detail
If the value of `stepSize_` is too large such that `totalSteps = (endTime - startTime) / stepSize = 1,uint256 currentStep = timePassed / stepSize=0,uint256 price = startPrice - (priceRange * currentStep / totalSteps)=startPrice`, the price of the NFT will remain unchanged.

## Impact
If the value of `stepSize_` is too large such that `totalSteps = (endTime - startTime) / stepSize = 1`, the price of the NFT will remain unchanged.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
    constructor(
        uint256 startPrice_,
        uint256 endPrice_,
        uint256 startTime_,
        uint256 endTime_,
        uint256 stepSize_
    ) { 
        // Cannot have 0 second steps
        require(stepSize_ > 0, "Step size must be greater than 0");
        // Duration must be a multiple of step size
        require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
        // Start price must be greater than end price
        require(startPrice_ > endPrice_, "Start price must be greater than end price");

        startPrice = startPrice_;
        endPrice = endPrice_;
        startTime = startTime_;
        endTime = endTime_;
        stepSize = stepSize_;
    }

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L106-L124
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


## Tool used

Manual Review

## Recommendation
Set the minimum and maximum values for `stepSize`, and perform checks on it.
