# [M] M-15 | Insuﬃcient msgOptions

## Summary
Severity: Medium
Contest weight: 0.0981
Dataset id: 2204
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
VaultCrossChainManager.sendMessage() will use the msgOptions mapping to determine what gas and value the executor should use for executing lzReceive on the destination chain. The values used is chosen based on the message's payloadType. However, they are the same for each chain. Some chains may require different parameters. While it may be fine for most EVM chains, sending messages to Solana is different. Instead of gas_limit and msg.value, the values used for Solana will be compute_units and lamports which is quite different. Reference: https://docs.layerzero.network/v2/developers/solana/gas-settings/options

## Recommendation
Consider having different msgOption values for different chains (or at least Solana).
