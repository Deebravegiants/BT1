# [C] AV-2 | Stale LLO Prices DoS

## Summary
Severity: Critical
Contest weight: 0.2084
Dataset id: 20523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Chainlink LLO prices are only updated during the opening and closing of rebalancing periods and the RequestHandler.executeRequest function. Yet, LLO prices are used in the logic for users to initiate withdraws/deposits on the AssetVault when previewing the deposit fee with the previewDepositFee function and previewing the withdrawal fee with the previewWithdrawalFee function.

Stale LLO prices, which users cannot update themselves, will cause users's withdraw/deposit initiations to revert as the withdraw/deposit fee estimation code checks that the LLO prices are no more stale than 1 Arbitrum block.

Additionally, protocol operators should update the latest LLO prices before calling the cycle or fulfillRequests functions during rebalance as these functions rely on up-to-date LLO prices.

## Recommendation
Do not rely on LLO pricing for the user-initiated deposits and withdrawals. Instead in the previewDepositFee and previewWithdrawalFee functions pass false as the useLlo value.
