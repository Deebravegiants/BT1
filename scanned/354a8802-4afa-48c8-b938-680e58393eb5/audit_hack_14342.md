# [M] Event `ClaimedProceeds` will always be emitted with zero balance

## Summary
Severity: Medium
Reporter: auditsea
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179
Type: audit-issue

## Details
# Event `ClaimedProceeds` will always be emitted with zero balance

## Summary
Event `ClaimedProceeds` will always be emitted with zero balance

## Vulnerability Detail
In `claimProceeds` function of `MeritDutchAuction.sol`, an event `ClaimedProceeds` is emitted with the contract's balance.
However, it is emitted after all balance is sent to the owner, so it will be always zero.

## Impact
The comment above event says it is used for off-chain integration, so the off-chain integration will be broken totally.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179

## Tool used

Manual Review

## Recommendation
Emit the event before sending ETH to the owner, or use a variable to store it and use it.
