# [C] GLOBAL-1 | shouldUnwrapNativeToken DoS

## Summary
Severity: Critical
Contest weight: 0.1599
Dataset id: 17870
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The shouldUnwrapNativeToken flag can be exploited by users to create positions that cannot be decreased by liquidations or ADL orders. For both liquidation orders and ADL orders the shouldUnwrapNativeToken flag is set to true, however the position can be created by a contract that is unable to receive the native token, causing the order execution to revert.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L274

## Recommendation
Refactor the shouldUnwrapNativeToken logic so that it cannot be used to determine whether or not transactions are able to succeed, and optionally set the shouldUnwrapNativeToken flag to false for liquidation and ADL orders.
