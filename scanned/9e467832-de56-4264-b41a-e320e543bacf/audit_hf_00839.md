# [M] M-09 | Incentives To Migrate Liquidatable Stakers

## Summary
Severity: Medium
Contest weight: 0.0516
Dataset id: 2575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While migration uses a significant amount of gas, there is no incentive to migrate liquidatable users. Only incentive is liquidation reward (50 tokens currently) which won't be sufficient especially when gas fees are high, hence liquidatable accounts won't be migrated.

## Recommendation
Reward the migrator if the migration is done for liquidatable account in the migrate() by at least gas fee they have to pay.
