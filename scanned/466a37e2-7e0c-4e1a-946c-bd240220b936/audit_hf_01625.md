# [H] Adding eETH as LRT will lead to accounting problems as eETH is a rebasing token

## Summary
Severity: High
Contest weight: 0.1658
Dataset id: 8731
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Based on the protocol's deployment scripts, it appears that the team intends to add eETH as an LRT. However, since eETH is a rebasing token, adding it as an LRT will lead to accounting issues because its balance continuously changes.
For example:
1. A user deposits 1.02 eETH today.
2. The protocol records the deposited amount as 1.02 eETH.
3. After one year, the user's deposited eETH amount increases to 1.10 eETH due to rebasing.
4. However, since the protocol still records only 1.02 eETH in its accounting, the user can only withdraw the initially deposited 1.02 eETH, losing their yield on eETH.

## Recommendation
Avoid using rebasing LRT tokens as collateral. Instead, only allow the wrapped versions of rebasing LRT tokens.
