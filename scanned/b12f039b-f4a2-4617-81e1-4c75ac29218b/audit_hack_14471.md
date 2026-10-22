# [M] Division by zero error if startTime equals endTime

## Summary
Severity: Medium
Reporter: rvdemonk
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78C42-L78C42
Type: audit-issue

## Details
# Division by zero error if startTime equals endTime

## Summary

Division by zero error if startTime equals endTime.

## Vulnerability Detail

No check exists in the constructor ensuring that startTime does not equal endTime. There is only a check ensuring that the duration of the auction is a multiple of stepSize. However, if the duration is zero, this check will be passed regardless of the value of stepSize.

## Impact

The value of totalSteps would equal zero, resulting in a division by zero error in the calculation of the price in getPriceAt. As a result every attempt to purchase a token in the auction would revert. 

Since there is no functionality present in the MeritNFT contract to transfer the Minter role, the MeritNFT contract would also essentially be bricked.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78C42-L78C42

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L117

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122

## Tool used

Manual Review

## Recommendation

Ensure that endTime - startTime > stepSize.
