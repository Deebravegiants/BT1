# [M] `MeritDutchAuction` allows for zero-duration auctions.

## Summary
Severity: Medium
Reporter: Bobface
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# `MeritDutchAuction` allows for zero-duration auctions.

## Summary
The `MeritDutchAuction` contract allows for zero-duration auctions.

## Vulnerability Detail
`MeritDutchAuction`'s [`constructor`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87) takes the `startTime_` and `endTime_` parameters specifying the auction's duration. The method does not check that `endTime_ > startTime_`, allowing for zero-duration auctions, i.e., auctions that have already ended on deployment.

The line `require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");` does not prevent this from happening, as when `endTime_ = startTime_`, the modulo will be zero for any `stepSize_`. 

## Impact
User error on deployment of an auction can cause the NFTs to be sold for the lowest possible price (`endPrice`).

## Code Snippet
```solidity
// contract MeritDutchAuction
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

## Tool used

Manual Review

## Recommendation
Check that `endTime_` is greater than `startTime_` in the `constructor`:
```solidity
require(endTime_ > startTime && stepSize_ > 0, "...")
```

If the existence of zero-duration auctions is intended, it should be made clear by ensuring `stepSize_ == 0`:
```solidity
require((endTime_ > startTime_  && stepSize_  > 0) || (endTime_ == startTime_  && stepSize_  == 0), "...")
```
