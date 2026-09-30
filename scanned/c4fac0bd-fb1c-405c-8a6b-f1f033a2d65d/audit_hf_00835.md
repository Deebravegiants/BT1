# [M] M-06 | Claim FeePool Rewards During Migration

## Summary
Severity: Medium
Contest weight: 0.1054
Dataset id: 2571
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unclaimed SNX rewards in V2X FeePool are rolled over each week and can be claimed by any debt shareholder. Some of the larger debt shareholders can claim an estimated 300 SNX each week, until all rolled over rewards are exhausted. During migration, liquidator rewards are claimed for the migrating account but these FeePool rewards are not. If the accounts are force migrated, they lose the opportunity to claim before migrating and cannot claim after as they would no longer hold debt shares. These rewards should be claimed as part of the migrating process to ensure all SNX owed to the account are moved to the V3 system.

## Recommendation
Be sure to inform users about how the migration will affect the FeePool rewards, and that they should either claim all fee pool rewards before the issuanceRatio is update to 1 wei, or after migrating.
