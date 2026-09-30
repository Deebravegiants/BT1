# [M] M-06 | Liquidation Gas Usage May Exceed Block Gas Limit

## Summary
Severity: Medium
Contest weight: 0.1575
Dataset id: 21434
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Based on the estimated gas usage conﬁgurations, the gas required to execute some decrease and liquidation orders may exceed the Avalanche block gas limit of 15,000,000 gas:
• Liquidation's gas usage itself: 4,000,000 (Decrease order gas limit)
• afterOrderExecution callback gas: 2,000,000
• Main payExecutionFee: 500,000
• 5 autoCancel order cancellation: 5 x 600.000 = 3,000,000
• 5 autoCancel order cancellation callback: 5,000,000
• 5 autoCancel payExecutionFee: 5 x 500,000 = 2,500,000
• In total = 17,100,000 which is 2,100,000 more than avalanche block gas limit. However in practice, it is unlikely that a liquidation will consume 15,000,000 or more gas units, refer to the attached PoC where we show that the rough maximum gas usage for a liquidation is around 14,000,000 gas. If liquidation execution can consume more than 15,000,000 gas units this would result in unliquidatable positions on the Avalanche network, which will introduce bad debt into the system.

## Proof of Concept
https://github.com/GuardianAudits/gmx-v2-1-team-2-pocs/tree/POC_GAS_USAGE

## Recommendation
Carefully consider this limit when making future code updates and modifying the refundExecutionFeeGasLimit as well as other gas conﬁgurations.
