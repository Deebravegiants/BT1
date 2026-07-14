# Q3789: sign_message_by_address trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `sign_message_by_address` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WalletRpcApi.sign_message_by_address` in `chia/wallet/wallet_rpc_api.py` executes a path where make `sign_message_by_address` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1899 `WalletRpcApi.sign_message_by_address`
- Entrypoint: RPC route `sign_message_by_address`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `sign_message_by_address` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/wallet_rpc_api.py:sign_message_by_address` and assert the receiving layer revalidates every security-critical field before trusting it
