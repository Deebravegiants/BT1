# [M] M-12 | Actions May Be Completed When Accounts Are Liquidatable By Margin Only

## Summary
Severity: Medium
Contest weight: 0.1002
Dataset id: 21130
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the BFP market actions are allowed to take place when an account involved is liquidatable by margin only, e.g. the account has a zero discounted margin value and a nonzero collateral value. Orders can be settled and positions can be merged and split to accounts that are liquidatable by margin only. This can lead to users errantly creating orders for accounts that are about to be liquidated, and thus having the orders cancelled. This behavior also introduces additional attack surface by allowing these accounts to be involved in such actions, which could potentially lead to unexpected scenarios.

## Recommendation
Consider validating that accounts are not liquidatable by margin only in the validateTrade, mergeAccounts, and splitAccount functions.
