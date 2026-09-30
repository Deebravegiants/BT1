# [C] C-05 | Negative Price Impact Bypassed For Consistent Profits

## Summary
Severity: Critical
Contest weight: 0.3046
Dataset id: 21110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can manipulate the skew to gain profit by making large orders and then merging them to use
the fill price penalty as a way to gain a profit. A position is opened with the fill price, where depending
on the skew the fill price can deviate from the actual price. That deviation is not realized when
opening the position, but left as unrealized PnL.
When merging 2 positions mergeAccounts calculates the margin only for the to address, and
assumes the from has no outstanding PnL. Then it adds its collateral and debt and sets the price to
the current oracle price.
The above enables us to:
1. Have a small position - 10 USD.
2. Make a new bigger position - 100k USD, using 1% of the skew.
3. Use the hooks and merge this new position (deleting the unrealized loss from the fill price
discount).
4. Our new position is at the current oracle price, but the skew is still there.
5. Close the position (lowering the skew) to claim the fill price incentive.
With the above example any user with enough capital can gain constant profits from the market,
while only paying order and keeper fees. Furthermore, the disincentive to imbalance longs and shorts
is bypassed.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs-2/blob/e07ea0bd231836fe37139d522b41df900e2e252e/markets/bfp-market/test/integration/modules/0x3b_POC.test.ts#L291

## Recommendation
Calculate any outstanding losses for the fromPosition based on the newly assigned
fromPosition.entryPrice and account for these in the newly merged to position.
