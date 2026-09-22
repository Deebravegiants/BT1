# [M] Missing input validation on constructor function parameters can lead to loss of value

## Summary
Severity: Medium
Reporter: Polaris_tow
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# Missing input validation on constructor function parameters can lead to loss of value

## Summary
Missing input validation on constructor function parameters can lead to loss of value
## Vulnerability Detail
There are some problems with the input validation in constructor（）, more specifically related to the timestamp values.
endTime_ can be much further in the future than startTime_, so  the auction may never end
Both endTime_ and startTime_ can be much further in the future, so auction might never start
Another scenario is when the value of endTime_-startTime_ is very small (almost equal), which is also an undesirable situation.
Those possibilities should all be mitigated.
## Impact
Missing parameter validation, the auction may never end and the auction may never start
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
## Tool used

Manual Review

## Recommendation
Perform more checks on the input parameters of the constructor function to avoid undesired and unreasonable auctions.
