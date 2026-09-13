# [M] The MeritDutchAuction contract allows startPrice and endPrice to be equal, resulting in a flat price auction.

## Summary
Severity: Medium
Reporter: radev_sw
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80
Type: audit-issue

## Details
# The MeritDutchAuction contract allows startPrice and endPrice to be equal, resulting in a flat price auction.

## Summary
The `MeritDutchAuction` contract allows `startPrice` and `endPrice` to be equal, resulting in a flat price auction.

## Vulnerability Detail
The `getPriceAt()` function calculates the current price based on the `startPrice` and `endPrice`, and the elapsed time since the start of the auction. If `startPrice` and `endPrice` are equal, the price will remain constant throughout the auction, essentially creating a flat price auction.

Also another possible issue related to validation:
The getPriceAt function calculates the current price based on the startPrice and endPrice, and the elapsed time since the start of the auction. If startTime and endTime are equal, the auction duration is effectively zero and every timestamp other than the exact start time would either be before the auction started or after it has ended.
This can prevent users from participating in the auction, since the auction will end the moment it starts. This could lead to unexpected behaviour if other parts of the contract or the overall system expect the auction to last for a certain duration.

## Impact
If other parts of the contract or the overall system expect the price to decrease over time, this could potentially cause issues. The exact impact will depend on the specifics of your system and use case.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L106-L124

## Tool used
Manual Review

## Recommendation
If flat price auctions are not a valid scenario for your use case, add a check in the constructor to ensure startPrice is strictly greater than endPrice. If they are a valid scenario, ensure that the rest of the contract's logic, and any external systems, handle this situation correctly.
