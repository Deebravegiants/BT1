# [M] M-08 | Order Fees Do Not Include Rebalance Costs

## Summary
Severity: Medium
Contest weight: 0.0681
Dataset id: 2238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _orderFee function the order fee computed does not include the fees to cover Perps V2 keeper fee to execute an order or the rebalance gas cost (if a rebalance is not triggered during the action) This is a one time hard cost that will be applied to every rebalance that occurs and is not speciﬁcally remunerated by the depositors/withdrawers who are triggering the rebalance.

## Recommendation
Consider if this is acceptable. If it is not, consider requiring that the actor who triggers the rebalance covers these fees.
