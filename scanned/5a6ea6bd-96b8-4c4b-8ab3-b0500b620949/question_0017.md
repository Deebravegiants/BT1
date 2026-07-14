# Q17: validate_block_merkle_roots reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots` and control pending roots, clear/cancel timing, and subsequent root submissions so that `validate_block_merkle_roots` in `chia/consensus/block_body_validation.py` executes a path where make `validate_block_merkle_roots` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/consensus/block_body_validation.py:158 `validate_block_merkle_roots`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `validate_block_merkle_roots` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/consensus/block_body_validation.py:validate_block_merkle_roots` and assert stale pending roots die cleanly
