# Q2169: add_lineage_proof cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_lineage_proof` and control batched updates across multiple store ids and roots so that `CATLineageStore.add_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where make `add_lineage_proof` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:32 `CATLineageStore.add_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_lineage_proof`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `add_lineage_proof` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/wallet/cat_wallet/lineage_store.py:add_lineage_proof` and assert no store commits under the wrong root
