# [M] User can make the bot pay gas fees for canceling dca orders instead.

## Summary
Severity: Medium
Reporter: n1punp
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L187-L199
Type: audit-issue

## Details
# User can make the bot pay gas fees for canceling dca orders instead.

## Summary
User can make the bot pay gas fees for canceling dca orders instead of themselves.

## Vulnerability Detail
- When the bot tries to execute dca order, the execution checks for 2 things:
  1. if the user has enough balance, and 2. if the allowance is enough.
  If both are not satisfied, then the execution will just cancel the order. 
- This means the order will be cancel if the user transfers out the tokens OR approving 0 to the contract. These 2 actions will cost cheaper gas than canceling the order directly, and the bot execution will just revert, leaving the bot to pay for the cleanup gas fees instead.

## Impact
- Bots can pay extra gas fees without getting anything in return.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L187-L199

## Tool used

Manual Review

## Recommendation
- Do not cancel order if the transaction conditions do not satisfy, to prevent the incentive for the user to try to cancel the position this way.
