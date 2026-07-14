# Q3770: get_coin_records_by_names trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `get_coin_records_by_names` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WalletRpcApi.get_coin_records_by_names` in `chia/wallet/wallet_rpc_api.py` executes a path where make `get_coin_records_by_names` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1753 `WalletRpcApi.get_coin_records_by_names`
- Entrypoint: RPC route `get_coin_records_by_names`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `get_coin_records_by_names` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/wallet_rpc_api.py:get_coin_records_by_names` and assert the receiving layer revalidates every security-critical field before trusting it
