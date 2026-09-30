# [C] ORDU-2 | Uncancellable/Unfreezable Order

## Summary
Severity: Critical
Contest weight: 0.1793
Dataset id: 17871
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the process of cancelling or freezing an order, the executionFee is paid to the keeper and a native token refund is issued to the user. However, the address of the user can point to a contract that is unable to accept the native token, causing the cancellation or freezing to revert. This way, the user may cause their order execution to revert and be retried until they wish their order to be executed – enabling risk free trades with knowledge of how the market moved after their order was created.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L336

## Recommendation
Consider refunding the user in WNT rather than the native token directly to avoid transaction manipulation.
