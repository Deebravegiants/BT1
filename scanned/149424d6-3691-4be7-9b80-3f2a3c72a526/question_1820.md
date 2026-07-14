# Q1820: join_pool trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `join_pool` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `PoolWallet.join_pool` in `chia/pools/pool_wallet.py` executes a path where make `join_pool` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/pool_wallet.py:629 `PoolWallet.join_pool`
- Entrypoint: pool wallet or singleton spend flow reaching `join_pool`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `join_pool` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/pools/pool_wallet.py:join_pool` and assert the receiving layer revalidates every security-critical field before trusting it
