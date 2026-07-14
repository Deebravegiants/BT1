# Q1783: update_pool_config trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `update_pool_config` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `PoolWallet.update_pool_config` in `chia/pools/pool_wallet.py` executes a path where make `update_pool_config` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/pool_wallet.py:231 `PoolWallet.update_pool_config`
- Entrypoint: pool wallet or singleton spend flow reaching `update_pool_config`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `update_pool_config` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/pools/pool_wallet.py:update_pool_config` and assert the receiving layer revalidates every security-critical field before trusting it
