# [H] H-09 | Asset Transfer During Liquidation Can Fail

## Summary
Severity: High
Contest weight: 0.2147
Dataset id: 21957
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During a liquidation, the afterOrderExecution function in the GmxUtils contract is responsible for sending the queue.tokenIn balance from the GmxUtils contract to the PerpetualVault contract. The problem is because the queue.tokenIn variable is set during the createOrder function’s specifically for a MarketIncrease order and is deleted in the afterOrderExecution or afterOrderCancellation functions. If a liquidation occurs when there is no MarketIncrease order in progress, the queue.tokenIn variable will be set to the zero address, causing the transfer of funds during liquidation to fail. As a result, these funds in the GmxUtils contract become stuck with no way to retrieve them, leading to losses for users, as they are not included in the PerpetualVault or GMX position and will not be accounted for in share calculations.

## Recommendation
The outputToken should be used from the eventData instead, similar to how it's done in the afterOrderExecution function. This ensures that the correct token address is used.
