# [M] Startime and endtime is not sufficiently validated in the constructor in MeritDutchAuction.sol

## Summary
Severity: Medium
Reporter: Jaraxxus
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# Startime and endtime is not sufficiently validated in the constructor in MeritDutchAuction.sol

## Summary

Starttime can be set in the past which will make the dutch auction factor useless. Endtime can also be set at the same time as starttime, which also makes the dutch auction factor not work.

## Vulnerability Detail

When creating the MeritDutchAuction contract, the owner can accidentally set the startime to be before block.timestamp because there is no check that starttime should not be able to set in the past. 

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

Auction can only start when startTime> block.timestamp. This means that if the starttime and endtime is set in the past, all auction will have the endPrice instead of the start price, which means that the Dutch auction is not working as intended.

```solidity
        // Auction must have started
        require(block.timestamp >= startTime, "Auction not started");
```

## Impact

Dutch auction is not working as intended

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

## Tool used

Manual Review

## Recommendation

Recommend adding the block.timestamp >= startTime and startTime != endTime check in the constructor
