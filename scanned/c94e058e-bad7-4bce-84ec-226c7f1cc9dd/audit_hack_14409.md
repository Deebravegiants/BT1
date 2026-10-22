# [H] A `malicious` auction contract `owner` can `avoid` an `auction` entirely.

## Summary
Severity: High
Reporter: 0xdice91
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68C4-L87C6
Type: audit-issue

## Details
# A `malicious` auction contract `owner` can `avoid` an `auction` entirely.

## Summary
The `stepSize` and `endTime` are not sufficiently validated, therefore a malicious auction contract owner can manipulate these values to avoid an auction.
## Vulnerability Detail
The auction owner can set any value of choice for `endTime` and `stepSize`. Therefore a malicious owner can set `endTime` to 2000 years from now and `stepSize` to 500 years or even set these values to far greater numbers. This undermines the whole Dutch auction as the `startPrice` will not drop in our lifetime. 
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
## Impact
This breaks the intentions of the developers as the auction is avoided and the malicious owner will be able to sell the NFT at a stable price. 
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68C4-L87C6
## Tool used
Manual Review

## Recommendation
Proper checks should be implemented on `endTime` to ensure that it is not a value too great, to avoid a stable price.
