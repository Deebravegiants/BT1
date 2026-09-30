# [C] C-01 | External Call Gas Adjustment DoS’s Liquidations

## Summary
Severity: Critical
Contest weight: 0.2376
Dataset id: 21421
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the clearAutoCancelOrder function the cancelOrder function is invoked from within the OrderUtils library, however the cancelOrder function will account for an external delegatecall being made as it subtracts gasleft() / 63 from the startingGas amount. No external call will be made as the cancelOrder function is being called from within the context of the OrderUtils file and therefore the cancelOrder function will be inlined in the clearAutoCancelOrder function. This errantly reduces the startingGas used to measure the gas expenditure for the keeper while cancelling autoCancel orders. As a result any attempt to cancel autoCancel orders will revert as the startingGas has been reduced such that it is now below the gasleft(). Therefore any positions with autoCancel orders cannot be closed as long as those orders exist, resulting in un-liquidatable positions.

## Proof of Concept
https://gist.github.com/owenThurm/b60e54087b3663d1994b07039bc71cf8

## Recommendation
Add a shouldAdjustStartingGas parameter to the cancelOrder function to account for when the cancelOrder function is invoked via delegatecall vs. function inlining.
