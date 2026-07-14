# Q15: validate_block_merkle_roots cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots` and control batched updates across multiple store ids and roots so that `validate_block_merkle_roots` in `chia/consensus/block_body_validation.py` executes a path where make `validate_block_merkle_roots` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/consensus/block_body_validation.py:158 `validate_block_merkle_roots`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `validate_block_merkle_roots` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/consensus/block_body_validation.py:validate_block_merkle_roots` and assert no store commits under the wrong root
