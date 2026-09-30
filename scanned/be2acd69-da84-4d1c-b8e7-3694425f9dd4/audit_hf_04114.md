# [H] ORDM-3 | Trapped collateralDelta With Increase Order

## Summary
Severity: High
Contest weight: 0.1404
Dataset id: 20574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a user creates an increase order and provides a deltaCollateral that is less than their openingFee, they cannot cancel this order and their funds will be stuck if the order cannot be executed. Additionally, there is no opening fee charged when a decrease or close order is cancelled. This is in contradiction to the behavior of increase orders.

## Recommendation
Refactor the way the opening fee is charged for increase, decrease and close orders. Consider requiring that the opening fee be provided up front in the modifyPosition function even for decrease or close orders. Alternatively, consider only charging the opening fee when an order is executed and instead maintaining a fraction of the executionFee. It would then be prudent to ensure that the executionFee is above a 0 or trivial amount.
