# [M] It is possible for owner to set `startTime_` greater than `endTime_` at deployment, which will break the protocol

## Summary
Severity: Medium
Reporter: SanketKogekar
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# It is possible for owner to set `startTime_` greater than `endTime_` at deployment, which will break the protocol

## Summary
Missing check in constructor to validate values: startTime_ & endTime_

## Vulnerability Detail

The constructor code clearly lacks the validation for `startTime_` and `endTime_` where inverted values could be passed and protocol will break. 

These values could not be changed ones the contract is deployed, and mistake will cause owner will need to redeploy the contract, and repay high deployment gas cost on mainnet.

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

## Impact

Not a serious issue, but most protocols won't miss that check.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87

## Tool used

Manual Review

## Recommendation

Add check:

```solidity
require(endTime_ > startTime_, "Invalid time values")
```
