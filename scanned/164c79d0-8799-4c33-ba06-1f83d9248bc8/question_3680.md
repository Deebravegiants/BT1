# Q3680: delete_all_keys trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `delete_all_keys` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WalletRpcApi.delete_all_keys` in `chia/wallet/wallet_rpc_api.py` executes a path where make `delete_all_keys` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:947 `WalletRpcApi.delete_all_keys`
- Entrypoint: RPC route `delete_all_keys`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `delete_all_keys` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/wallet_rpc_api.py:delete_all_keys` and assert the receiving layer revalidates every security-critical field before trusting it
