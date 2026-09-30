# [M] GLOBAL-6 | Block Stuffing Attack

## Summary
Severity: Medium
Contest weight: 0.1069
Dataset id: 18181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Order execution takes ~2,000,000 gas units for a vanilla execution without a swapPath or callbackContract. On certain chains, such as Avalanche C-chain, the block gas limit can be close to how much gas it takes for order executions. This makes the protocol susceptible to a block stuffing attack. For example, this [transaction](https://testnet.snowtrace.io/tx/0x6d987a1cd616c09c6658db7ca0ae16fcea1482a4a6536a1b945571dce30372b2) on the Avalanche Fuji testnet took over 4,000,000 gas units which is greater than 50% of the gas limit of 8,000,000. An attacker may choose to stuff blocks to delay the execution of their order until the current price moves favorably.

## Recommendation
Consider gas optimization strategies alongside measures to remove stale execution tx’s from the mempool to prevent such manipulations.
