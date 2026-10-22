# [H] ORDM-2 | Position Created Without Reserves

## Summary
Severity: High
Contest weight: 0.1394
Dataset id: 20573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user’s position is created without taking the funds in the Vault into account. As a result, a trader may open a position when the Vault has zero funds, or not enough funds to support the market’s PnL. Users will be unable to realize their profits and be stuck with their position. Furthermore, as soon as there are enough reserves in the Vault for withdrawal, the Vault’s funds will be drained and LP’s will lose their deposited funds.

## Recommendation
Validate that the open interest does not exceed some percentage of the Vault’s funds. This would create a buffer and help avoid a scenario where the pool does not have enough liquidity to support user profits.
