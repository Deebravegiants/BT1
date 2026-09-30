# [M] M-2 The use of tx.origin

## Summary
Severity: Medium
Contest weight: 0.0527
Dataset id: 7116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidity gauge manager is set as a tx.origin of the gauge deploy transaction.
• LiquidityGauge.vy#L176
It is not recommended to have tx.origin in access control logic. Some DeFi users are Multisigs or Account Abstraction wallets. In such cases, tx.origin is not correct ﬁnal user identiﬁcation.

## Recommendation
We recommend having manager as a customizable input for factory.deploy_gauge().
