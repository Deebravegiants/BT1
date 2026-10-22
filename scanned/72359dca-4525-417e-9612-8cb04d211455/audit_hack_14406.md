# [M] Missing stepSize_ validation

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# Missing stepSize_ validation

## Summary

## Vulnerability Detail
`MeritDutchAuction` constructor misses to validate the value of `stepSize_` comparing to the delta of `startTime_` and `endTime_`

`stepSize_` is the duration of the each pricing step. Accordingly the constructor validates that the duration should be multiple of stepSize to avoid truncation/precision loss in pricing.
So the requirement was done as below;

```solidity
78: require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
```

However, it's not checked `require(stepSize_ < endTime_ - startTime_)`.

If the `stepSize_` is set as `stepSize_ > (endTime_ - startTime_)` the first % requirement will pass and it will end-up the unwanted situation below;
Once the auction starts, the `mint` function will revert as the `getPriceAt` function below will panic,

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
        uint256 totalSteps = (endTime - startTime) / stepSize;//<---- @audit totalSteps will be 0
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);//<---- @audit panic here due to totalSteps
        return price;
    }

```
As there's no pausing mechanism, the time will pass and it will come to the condition `time >= endTime`. 
At this moment the `mint` function will serve normally but the NFT prices will be the `endPrice`. This will end up the NFTs being sold to the lowest price.

## Impact
NFT's will be sold to the bottom price
## Code Snippet
```solidity
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
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87)


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
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L106-L124)

## Tool used

Manual Review

## Recommendation
Validate the `stepSize_` as `require(stepSize_ < endTime_ - startTime_)`
