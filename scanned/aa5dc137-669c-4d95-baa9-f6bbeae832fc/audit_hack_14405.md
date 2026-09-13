# [H] No check in the constructor for endTime_ == startTime_, causing a divide by 0.

## Summary
Severity: High
Reporter: dopeflamingo
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# No check in the constructor for endTime_ == startTime_, causing a divide by 0.

## Summary

Currently the only check for the start and end time of the auction is whether the duration of the auction is a multiple of the ```stepSize_```. This also mitigates the fact that the auction endTime cannot be before the startTime. However this doesn't stop the endTime == startTime.

## Vulnerability Detail

Since the check is ```(endTime_ - startTime_) % stepSize_ == 0```, this will always pass when endTime_ = startTime_. As 0 modulo of any number is still 0.

## Impact
This can break core functionality of the contract, particularly in the ```getPriceAt``` function. ```totalSteps``` on line 122 will always be of value 0. meaning on line 123 the price returned will throw a revert error, as the function won't be able to return any price meaning no NFTs can be minted. 

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122-L123

## Tool used

Manual Review, Foundry

## Recommendation

Use the following check in the constructor just to be safe. ```require(endTime_ > startTime_, "End time of auction must be in the future");```.
