# [M] `startTime` can be in the past

## Summary
Severity: Medium
Reporter: immeas
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L75-L80
Type: audit-issue

## Details
# `startTime` can be in the past

## Summary
Due to lack of `startTime` validation an auction can start late. This would potentially lessen proceeds gained by the auctioneer.

## Vulnerability Detail
When creating an auction a couple of inputs are validated:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L75-L80
```solidity
File: MeritDutchAuction.sol

75:        // Cannot have 0 second steps
76:        require(stepSize_ > 0, "Step size must be greater than 0");
77:        // Duration must be a multiple of step size
78:        require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
79:        // Start price must be greater than end price
80:        require(startPrice_ > endPrice_, "Start price must be greater than end price");
```

There is however no validation that the `startTime` is in the future.

This protocol is intended for [mainnet](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/README.md#q-on-what-chains-are-the-smart-contracts-going-to-be-deployed) and its not uncommon for mainnet to be clogged. Thus a launch of the auction might be delayed and `startTime` passed.

Imagine an influencer wanting to do a "from nowhere" flash release of a new NFT collection. They go out on social media: "ITS OUT NOW!!!" at the same time they deploy the auction together with the NFT (and necessary setup). Mainnet however is clogged and they didn't provide a high enough tip to be included very fast. Thus their auction is included in a block too late and starts at a lower price than intended.

### PoC test
in `MeritDutchAuction.t.sol`
```solidity
    function testAuctionStartLate() public {
        vm.warp(startTime + 1 hours);
        
        vm.prank(owner);
        MeritDutchAuction _auction = new MeritDutchAuction(
            START_PRICE,
            END_PRICE,
            startTime,
            endTime,
            STEP_SIZE
        );

        // auction starts at a lower price
        assertLt(_auction.getPrice(),START_PRICE);
    }
```

## Impact
The auction could start at a lower price than the owner intended, losing out on early buyer proceeds.

## Code Snippet
See above.

## Tool used
Manual Review

## Recommendation
Add a validation that the `startTime` is in the future:

```diff
+       // startTime must be in the future
+       require(startTime_ > block.timestamp,"startTime must be in the future");
        // Duration must be a multiple of step size
        require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
```
