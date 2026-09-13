# [M] `MeritDutchAuction` allows for already started auctions to be created

## Summary
Severity: Medium
Reporter: Bobface
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# `MeritDutchAuction` allows for already started auctions to be created

## Summary
The `MeritDutchAuction` contract allows for already started auctions to be created.

## Vulnerability Detail
`MeritDutchAuction`'s [`constructor`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87) takes the `startTime_` parameter specifying the timestamp of the auction's start. The method does not check that `startTime_ > block.timestamp`, meaning an auction that has been started in the past can be created.

## Impact
The exploitation of this behaviour is rather unlikely but possible. In a scenario where an auction for a popular NFT is submitted to the mempool, attacker(s) can use techniques such as block stuffing to delay the execution of the contract deployment. Since the price automatically decreases over time, the NFTs will be immediately available at a lower price than intended when the contract is deployed.  User error, where a  `startTime_` in the past is supplied by accident can also cause this issue.


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
Check for `startTime_ > block.timestamp` in the `constructor`.
