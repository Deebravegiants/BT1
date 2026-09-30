# [M] OstiumPriceUpKeep::performUpKeep() does not correctly handle possible reverts

## Summary
Severity: Medium
Contest weight: 0.0770
Dataset id: 11140
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OstiumPriceUpKeep::performUpKeep() should unregister pending market orders or disable triggers and pending limit orders if the execution fails. However, it is not dealing with all the revert scenarios, for example:
1. Not enough value to pay for the verifier.
2. Invalid prices.

## Recommendation
If performUpKeep() reverts due to one of these reasons, the protocol should be protected and make users pay for it.
If it does not have enough value to pay for the verifier or the prices are invalid, the corresponding user should still pay the oracle fees. Additionally, before calling OstiumPriceUpKeep::getPrice(), a check should be in place to ensure the contract will have enough eth to pay for performUpkeep().
Instead of reverting, it should also unregister the orders and the triggers to allow faster replayability.
