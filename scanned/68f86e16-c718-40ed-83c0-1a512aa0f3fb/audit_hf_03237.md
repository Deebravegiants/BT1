# [H] ORDH-2 | Frozen Order Execution Loop

## Summary
Severity: High
Contest weight: 0.1707
Dataset id: 17856
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the execute order feature is blocked, all non-market orders will become frozen rather than being cancelled. This could potentially spur on an infinite loop of execution for the frozen order keeper without any remuneration for gas costs. Additionally, loops of continually failing frozen orders like this could occur from a number of errors caused during order execution.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L2039

## Recommendation
Consider cancelling all orders or simply reverting when the execute order feature is blocked. Additionally take special care around the frozen order keeper logic to avoid costly infinite loops of frozen orders–and consider requiring an executionFee for additional executions of orders after they are frozen.
