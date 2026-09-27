# [M] [MEDIUM] MeritDutchAuction - Missing endTime < startTime check causing the price to always be the endPrice

## Summary
Severity: Medium
Reporter: vangrim
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68
Type: audit-issue

## Details
# [MEDIUM] MeritDutchAuction - Missing endTime < startTime check causing the price to always be the endPrice

## Summary
In the **`MeritDutchAuction`** contract, a check is missing which ensures that the **`endTime`** is greater than the **`startTime`**. The absence of this check could result in the price always being equal to **`endPrice`**.

## Vulnerability Detail
In a Dutch auction, the price is supposed to decrease from the **`startPrice`** to the **`endPrice`** over a certain time period, represented by **`startTime`** and **`endTime`**. However, if **`endTime`** is not strictly greater than **`startTime`**, the auction could start and end at the same moment, causing the price to be always equal to the **`endPrice`**.

## Impact
The consequence is a significant deviation from the desired Dutch auction behavior, potentially impacting fair pricing and participation. Instead of a decreasing price mechanism over time, participants would always see the **`endPrice`**, which could discourage potential bidders, skew auction outcomes, and ultimately distort the intended market mechanisms of the contract.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68

## Tool used

Manual Review

## Recommendation
To fix this issue, ensure the **`endTime`** is strictly greater than **`startTime`**. Here's the corrected function:

```solidity
function startAuction(
    uint256 _tokenId,
    uint256 _startPrice,
    uint256 _endPrice,
    uint256 _startTime,
    uint256 _endTime
) external onlyOwner {
    require(_endTime > _startTime, "End time must be greater than start time");
    ...
}
```
