# [M] Users can be forced to claim assets at bad

## Summary
Severity: Medium
Contest weight: 0.1095
Dataset id: 20072
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In balanced vault contract, anyone can call claim assets for other accounts; malicious users could abuse this function to force other users to receive less assets than they expect.

When claiming asset, pro rate, in which users will receive less assets than expect, will be applied when total collateral is less than total unclaimed amount. So after redeeming shares and converting it to assets, users might not want to claim assets right away in this scenario, for they will receive less token amount. However, other users can force them to claim via claim() function because there is no restrict on this function to claim for other accounts.

Users will be forced to receive less assets in some scenarios.

## Recommendation
Only account owner (msg.sender == account) can claim asset for their account.
