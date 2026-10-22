# [M] Missing checks in the constructor of `MeritDutchAuction.sol` can let users get NFT for free

## Summary
Severity: Medium
Reporter: ret2basic.eth
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# Missing checks in the constructor of `MeritDutchAuction.sol` can let users get NFT for free

## Summary

The constructor in `MeritDutchAuction.sol` misses check on `endTime_`. If `endTime_ = 0` is used, users can wait until right before the auction end time to get NFT for free.

## Vulnerability Detail

The constructor in `MeritDutchAuction.sol` does have have check on `endTime_`:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

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

If `endTime_ = 0` is used, users can wait until right before the auction end time to get NFT for free:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L112-L114

```solidity
        if(time >= endTime) {
            return endPrice;
        }
```

## Impact

Users can get NFT for free.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

## Tool used

Manual Review

## Recommendation

Set a lower bound for `endTime_`, or at least check it is greater than 0.
