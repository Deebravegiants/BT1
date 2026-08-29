# [M] Multiple lien positions liquidations could cause fund loss

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/261
Type: sherlock-finding

## Details
__141345__

medium

# Multiple lien positions liquidations could cause fund loss

## Summary

1 collateral NFT can have multiple loan positions. When liquidated, these positions will be bundled together and could incur loss to the LP if the liquidation auction does not go well.


## Vulnerability Detail

Consider the following case:
A collateral is taking 2 different loan, 1 for a private vault with duration of 15 days for $100, 1 for a public vault with duration of 30 days for $1,000.

If after 15 days, the loan is not paid back, it will be liquidated. According to the currently rule, the other unexpired loan will also get involved, since the underlying collateral is the same.

But the auction goes without bidder or very low bid, at the end no fund or low amount of fund will be collected for the defaulted loan.
The lenders for the other positions will incur loss.


## Impact

Some lenders could have loss of fund due to the other position separated from the loan they have.


## Code Snippet

As long as one of the positions does not paid back, all the positions associated with the collateral will be liquidated.

https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/AstariaRouter.sol#L362-L374


## Tool used

Manual Review


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/261_
