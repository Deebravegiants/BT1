# [M] M-07 | GLV Trapped Funds Upon Disabled

## Summary
Severity: Medium
Contest weight: 0.0730
Dataset id: 21911
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the createGlvWithdrawal function the validateGlvMarket validation uses true as the shouldBeEnabled configuration. Therefore users may not withdraw from the portion of a Glv that is a disabled Glv market. As a result when a market becomes disabled via the isGlvMarketDisabledKey key, users are not able to fully withdraw their deposited value from the Glv unless the keeper explicitly shifts all funds out of the disabled Glv market.

## Recommendation
Consider allowing users to withdraw a disabled glv market, but not deposit it.
