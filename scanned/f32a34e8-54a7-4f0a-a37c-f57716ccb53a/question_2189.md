# Q2189: remove_lineage_proof trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage_proof` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `CATLineageStore.remove_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where make `remove_lineage_proof` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:40 `CATLineageStore.remove_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage_proof`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `remove_lineage_proof` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/cat_wallet/lineage_store.py:remove_lineage_proof` and assert the receiving layer revalidates every security-critical field before trusting it
