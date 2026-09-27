# [?] Fix plugin context zeroing, erc1155 underflow, screen overflow, and mainnet gate

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-08-10
Source: https://github.com/LedgerHQ/app-ethereum/commit/704aa1c16f1cdce87f50ff13836b1a6aa6dcdce0
Type: security-commit

## Details
Fix plugin context zeroing, erc1155 underflow, screen overflow, and mainnet gate

- pluginContext not zeroed on INIT_CONTRACT:
The 1 024-byte pluginContext scratch buffer is shared across plugin
registrations. erc721, erc1155, and eth2 now call explicit_bzero on
the cast context at the top of their INIT_CONTRACT handler so no
previous plugin's state leaks into the new invocation.

- ids_array_len underflow in erc1155 batch parsing:
When safeBatchTransferFrom carries an empty ids array (len == 0) the
previous code decremented ids_array_len via --ids_array_len before
reaching 0, wrapping the uint16_t to 65 535 and corrupting subsequent
parsing. next_param now goes directly to VALUE_LENGTH when
ids_array_len == 0.

- erc1155 screen count can overflow uint8_t:
Added a compile-time _Static_assert to catch this at build time, and
a runtime bounds check in set_batch_transfer_ui that returns
ETH_PLUGIN_RESULT_ERROR if pair_idx >= ERC1155_BATCH_DISPLAY_MAX.

- eth2 / eip7002 / eip7251 lack Ethereum mainnet gate:
The ETH2 deposit contract, the EIP-7002 withdrawal predeploy, and the
EIP-7251 consolidation predeploy are all Ethereum-mainnet-only. Their
FINALIZE handlers now verify get_tx_chain_id() == ETHEREUM_MAINNET_CHAINID
and return ETH_PLUGIN_RESULT_ERROR on any other chain.

Unit tests added for every new security property.
