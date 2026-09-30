# [H] DOU-2 | Decrease Order Gas Attack

## Summary
Severity: High
Contest weight: 0.2074
Dataset id: 17854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the sizeDeltaUsd of a LimitDecrease order exceeds the position sizeInUsd, the order lives on in the orderStore and the executionFee is set to 0. This can lead to a potential gas vamp attack on the keeper, where a user continually submits increase orders to create small positions to be decreased by a LimitDecrease order that remains in the orderStore. Each execution of the LimitDecrease order can be arbitrarily expensive due to callbacks and the keeper would receive no remuneration for a potentially large amount of gas expenditure. An orchestrated attack like this could drain the keeper of its native tokens and shut down all execution on the exchange.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1864

## Recommendation
Require an executionFee for additional executions of LimitDecrease orders.
