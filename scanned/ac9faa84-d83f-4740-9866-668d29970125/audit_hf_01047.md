# [H] MJR-2 Wrongly calculated ETH amount to transfer

## Summary
Severity: High
Contest weight: 0.0375
Dataset id: 4010
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At lines ProfitSplitter.sol#L198-L205 contract swaps whole splitterIncomingBalance to ETH if splitterIncomingBalance insufficient to cover gap between splitterEthBalance and amount, in other words contract try to get as much as closer to amount ETH amount. However as we can see in this block of code contract assigns amountsOut[1] to amount, it's wrong because we need to assign splitterEthBalance.add(amountsOut[1])

## Recommendation
We recommend to assign splitterEthBalance.add(amountsOut[1]) to amount instead of amountsOut[1]
