# [H] Validation is required for both `startTime_` and `endTime_` parameters

## Summary
Severity: High
Reporter: blackhole
Source: https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L68
Type: audit-issue

## Details
# Validation is required for both `startTime_` and `endTime_` parameters

## Summary
There is no validation of `startTime_` and `endTime_` in the constructor of the `MeritDutchAuction` contract.
If the `startTime_` is equal to `endTime_`, this contract doesn't work.
And also need to check `startTime_` is greater than `block.timestamp` and `endTime_` is greater than `startTime_`.


## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L68

```solidity
File: src/MeritDutchAuction.sol#L68
    constructor(
        uint256 startPrice_,
        uint256 endPrice_,
        uint256 startTime_,
        uint256 endTime_, 
        uint256 stepSize_
    ) { 
        // Cannot have 0 second steps
        require(stepSize_ > 0, "Step size must be greater than 0"); // @audit-info recommend MIN_STEPSIZE
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

## Impact

If the startTime_ and endTime_ are invalid, the whole contract doesn't work after being created.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L68

## Tool used

Manual Review

## Recommendation

Recommend adding validation steps to check `startTime_` and `endTime_` parameters.

```solidity
File: src/MeritDutchAuction.sol#L41
    constructor(
        uint256 startPrice_,
        uint256 endPrice_,
        uint256 startTime_, // @audit no validation startTime > block.timestamp
        uint256 endTime_, // @audit-info validation endTime > startTime : revert in duration check
        uint256 stepSize_
    ) { 
        // Cannot have 0 second steps
        require(stepSize_ > 0, "Step size must be greater than 0"); // @audit-info recommend MIN_STEPSIZE
        
        // @audit here
        require(startTime_ > block.timestamp, "starTime error");
        require(startTime_ < endTime_, "endTime error");

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
