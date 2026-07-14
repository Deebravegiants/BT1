# Q871: add_compact_proof_of_time cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_compact_proof_of_time` and control batched updates across multiple store ids and roots so that `FullNode.add_compact_proof_of_time` in `chia/full_node/full_node.py` executes a path where make `add_compact_proof_of_time` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node.py:3241 `FullNode.add_compact_proof_of_time`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_compact_proof_of_time`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `add_compact_proof_of_time` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/full_node/full_node.py:add_compact_proof_of_time` and assert no store commits under the wrong root
