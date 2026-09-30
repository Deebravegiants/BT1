# [M] M-16 | Risk Free Arbitrage Attack

## Summary
Severity: Medium
Contest weight: 0.1091
Dataset id: 21507
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The main market making operations allow the protocol to rebalance the liquidity and bump the floor price, as long as solvency is maintained. Due to the fact that these operations can be executed in the same transaction, there is an arbitrage attack opportunity that will drain most of the initial reserves from the protocol, without any risk. Consider the following attack flow:
1. buy bAssets, pushing the price deep into DISCOVERY
2. trigger a sweep to distribute the surplus reserves into the ANCHOR and FLOOR ranges, and update checkpoint tick
3. call bump multiple times to catch up with the active tick.
4. sell all bAssets at a profit, removing a huge chunk of reserves liquidity.

## Recommendation
Limit the amount of times the liquidity operations can be called within a block, or limit it to once every few blocks.
