# [M] No checks for L2 Sequencer being down

## Summary
Severity: Medium
Contest weight: 0.1090
Dataset id: 21988
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** Neither `PriceFeed.sol` (which is designed to work with Chainlink) nor `StorkOracleWrapper` (which has been created to allow `PriceFeed` to work with Stork Oracles) implement a check to test whether the L2 Sequencer is currently down.

When using Chainlink or other oracles with L2 chains like Arbitrum, smart contracts should [check whether the L2 Sequencer is down](https://medium.com/Bima-Labs/chainlink-oracle-defi-attacks-93b6cb6541bf#0faf) to avoid stale pricing data that appears fresh.

** Code can execute with prices that don’t reflect the current pricing resulting in a potential loss of funds for users or the protocol.

## Recommendation
** Chainlink’s official documentation provides an [example](https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code) implementation of checking L2 sequencers. Stork's publicly available documentation does not provide any such feed.
