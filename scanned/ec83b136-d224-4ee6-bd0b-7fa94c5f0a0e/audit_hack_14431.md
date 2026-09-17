# [M] Immutables should be in uppercase in MeritDutchAuction.sol

## Summary
Severity: Medium
Reporter: V1235813
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L17-L25
Type: audit-issue

## Details
# Immutables should be in uppercase in MeritDutchAuction.sol

## Summary
Immutables should be in uppercase  in MeritDutchAuction.sol

## Vulnerability Detail
Immutables should be in uppercase in MeritDutchAuction.sol
variable startPrice, endPrice, startTime, endTime, stepSize should be in uppercase

## Impact
Immutables should be in uppercase in MeritDutchAuction.sol

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L17-L25


    uint256 public immutable startPrice;
    // Price at the end of the auction in wei
    uint256 public immutable endPrice;
    // Start time of the auction as a unix timestamp
    uint256 public immutable startTime;
    // End time of the auction as a unix timestamp
    uint256 public immutable endTime;
    // Duration of each step in seconds
    uint256 public immutable stepSize;

## Tool used

Manual Review

## Recommendation
Immutables should be in uppercase in MeritDutchAuction.sol
variable startPrice, endPrice, startTime, endTime, stepSize should be in uppercase
