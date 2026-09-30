# [C] Anyone can spend others XP by calling spendXP

## Summary
Severity: Critical
Contest weight: 0.0261
Dataset id: 16288
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In VaronveStaking there's a call spendXP: Which, as the name suggests, spends XP for the user. This is called from levelUP and buyTicket to spend cost for the action. The issue however is that spendXP is public. Hence it can be called by anyone, letting any user spend XP for any other user.

## Recommendation
Consider making spendXP internal instead of public:
