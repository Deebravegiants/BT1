# [M] M-06 | Different Gas Limits May Lead To DOS

## Summary
Severity: Medium
Contest weight: 0.1095
Dataset id: 1990
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Different chains have different gas limits. Due to the fact that a user can send as many tokens as they have using releaseOnEid, it may be possible that the tx has enough gas limit on the source chain, but not enough gas Limit to execute on destination chain. For example ETH Mainnet gas limit is 30M, however Avalanche C-chain is 15M, half the gas limit. This can lead to permanently stuck NFT's when the execution of the _lzReceive will exceed the max block gas limit and any retry attempts will fail. This issue may be more prevalent on chains with an even lower gas limit such as some chains have as low as 8M gas limit. This small of a gas limit can be reached with about 57 tokens being sent.

## Recommendation
It is recommended to add a limit of 10-20 on the amount of NFTs that can be bridged in a single tx.
