# [M] Important Check missing in MeritDutchAuction.sol

## Summary
Severity: Medium
Reporter: 3agle
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87:
Type: audit-issue

## Details
# Important Check missing in MeritDutchAuction.sol

## Summary
The MeritDutchAuction contract is missing an important check in its constructor that ensures the start time is less than the end time. This missing check can allow the owner to set the start time equal to the end time, which defeats the purpose of the Dutch auction.

## Vulnerability Detail
In the constructor of the MeritDutchAuction contract, there are various checks in place for the start time, end time, start price, end price, and step size. However, the crucial check `startTime < endTime` is not included.

## Impact
The absence of the check `startTime < endTime` allows the owner to set the start time (`startTime_`) equal to the end time (`endTime_`). This can undermine the Dutch auction mechanism's intended functionality.

## Code Snippet
The vulnerable code snippet can be found at https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87:
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

## Tool used
Manual Review & Foundry

## Recommendation
To address this vulnerability, the code should be modified as follows:
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
        // Add this check to enforce the invariant
        require(startTime_ < endTime_, "Start Time must be less than End Time");

        startPrice = startPrice_;
        endPrice = endPrice_;
        startTime = startTime_;
        endTime = endTime_;
        stepSize = stepSize_;
    }
```

By adding the `require(startTime_ < endTime_, "Start Time must be less than End Time")` check, the vulnerability can be mitigated, ensuring that the start time is always set to a value earlier than the end time in the Dutch auction.
