# [H] H-05 | Migration Process Can Be DoS’d

## Summary
Severity: High
Contest weight: 0.2495
Dataset id: 21500
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the migration process, the protocol will: 1. Initialize the pool 2. Distribute spot tokens and create credits 3. Deploy liquidity to the pool This migration is not atomic and will take some time, which means there will be a lag between the initialization of the Uniswap pool and deploying liquidity to the pool. In this period, an attacker can add liquidity to any tick he wants, perform a swap, and change the active tick. Since the pool is empty, this can be done with only a few wei. Attacker injects a swap between steps 1 and 3 above but the migration process continues, and there is no check regarding whether the current tick is the same as INITIAL_ACTIVE_TICK. There are two possible impacts depending on which way the swap is performed by the attacker. 1. If the attacker swaps below the floor tick, the liquidity deployment will be successful, but the ratio between discovery and anchor will be enormous. 2. If the attacker swaps way above, liquidity deployment will fail due to active tick being in the discovery range.

## Recommendation
Consider refactoring the migration process such that there is no time window for swaps to occur between the initialization of the pool and deploying liquidity to the pool.
