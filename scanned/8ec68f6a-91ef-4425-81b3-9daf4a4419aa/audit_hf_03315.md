# [C] ORDU-1 | Unbounded swapPath Length

## Summary
Severity: Critical
Contest weight: 0.1902
Dataset id: 18166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an order there is no validation that the swapPath is under a certain max length. This allows malicious users to create risk-free trades on the exchange. Notably, among other ways, a trader may submit a MarketIncrease order with a swapPath that puts the order just over the block gas limit when combined with a callback that consumes nearly the entire maxCallbackGasLimit. When a trader wishes the trade to be executed using outdated prices, they can toggle the callback contract to only consume a very small amount of gas, enabling the order to be executed and recorded in a block.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/ORDU_1.ts

## Recommendation
Add validation on the max length for the swapPath of orders to protect the exchange from the entire class of swapPath gas manipulation attacks.
