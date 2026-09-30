# [C] ORDU-1 | Cancelled Order In beforeOrderExecution Callback

## Summary
Severity: Critical
Contest weight: 0.1695
Dataset id: 17864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the beforeOrderExecution callback it is possible to cancel the order prior to processing which returns funds to the user and removes the order from the orderStore. However, the order will still execute and create a position with the initial collateral delta and USD size. This results in a deficit in the orderStore balances which causes accounting issues across the entire exchange.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L183

## Recommendation
Do not allow order cancellation to occur during the execution of that order, possibly by moving the cancelOrder function to the orderHandler and allowing NonReentrant modifiers to resolve this issue. Furthermore, ensure consistency between storage and cached parameters.
