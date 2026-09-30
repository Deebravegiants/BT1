# [M] CHAIN-1 | Hardcoded Chain ID

## Summary
Severity: Medium
Contest weight: 0.0738
Dataset id: 18506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Chain.sol file, uint256 constant public ARBITRUM_CHAIN_ID = 42161; is hardcoded.
From a comment in Oracle.sol, the codebase wishes to be impervious to a change in the chain ID:
// it might be possible for the block.chainid to change due to a fork or similar
However in the event that the Arbitrum chain ID changes, the currentBlockNumber and getBlockHash
functions will not return the appropriate Arbitrum values, potentially causing drastic effects on the
exchange.

## Recommendation
Add a configurable chain ID for Arbitrum.
