# [M] ORDM-8 | Positions Can Be Liquidated In A Paused Market

## Summary
Severity: Medium
Contest weight: 0.0855
Dataset id: 20556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidating a position, by calling the function liquidatePosition from the OrderManager contract, does not check if the market in which the order was placed is currently paused or not. Any already existing positions can be liquidated but users cannot cancel or add to them during pause by design. Another issue that appears when a liquidation is done on an order in a paused market is triggering market fee payment. This takes place as the function updateCumulativeFees from the DataFabric will get called.

## Recommendation
Add a call to the _validateMarket function at the beginning of the _liquidatePosition function in the OrderManager contract.
