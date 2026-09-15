# [M] No deadline for `DcaOrder`

## Summary
Severity: Medium
Reporter: n1punp
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L334
Type: audit-issue

## Details
# No deadline for `DcaOrder`

## Summary
No deadline for `DcaOrder` 

## Vulnerability Detail
`DcaOrder` does not contain any deadline information on the order. There are 2 main potential scenarios where this can cause issues:
1. This can lead to tx being stuck in the mempool and only get executed when the tx becomes in favor of the executor. (although there's slippage control and twap usage, but this is not effective).
2. when the user transfers out the token out of the wallet -> causing the dca execution to revert. Later on, the user deposits the tokens back in for normal usage, this will then make the execution become enabled again (even if the user has forgotten about it). This is, in fact, similar to Opensea's issue on transferring out NFT and leaving the order approval remained.

## Impact
- The users can have their orders get executed in an untimely manner without proper deadline set.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L334

## Tool used

Manual Review

## Recommendation
- Add deadline to the order.
