# Q2161: remove_lineage trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_lineage` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `CATWallet.remove_lineage` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where make `remove_lineage` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:815 `CATWallet.remove_lineage`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_lineage`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `remove_lineage` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/cat_wallet/cat_wallet.py:remove_lineage` and assert the receiving layer revalidates every security-critical field before trusting it
