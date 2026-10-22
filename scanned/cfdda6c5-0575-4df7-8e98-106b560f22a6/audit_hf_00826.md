# [H] H-05 | Migrations Can Be Executed Even If Paused

## Summary
Severity: High
Contest weight: 0.1684
Dataset id: 2562
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LegacyMarket.migrate()](https://github.com/Synthetixio/synthetix-v3/blob/2ea4dd99d5344b38df7b695f255216958bf3b086/markets/legacy-market/contracts/LegacyMarket.sol#L179C1-L181C10) reverts if pauseMigration = true. However, there is another function for migrations which lacks this check - [migrateOnBehalf()](https://github.com/Synthetixio/synthetix-v3/blob/2ea4dd99d5344b38df7b695f255216958bf3b086/markets/legacy-market/contracts/LegacyMarket.sol#L189C1-L192C1). Anyone can call migrateOnBehalf and pass their address to execute a migration even when they are paused.

## Recommendation
Move the check for paused migrations in the internal [_migrate()](https://github.com/Synthetixio/synthetix-v3/blob/2ea4dd99d5344b38df7b695f255216958bf3b086/markets/legacy-market/contracts/LegacyMarket.sol#L196-L288) function
