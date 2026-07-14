# Q2717: create_merkle_proof reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_merkle_proof` and control pending roots, clear/cancel timing, and subsequent root submissions so that `create_merkle_proof` in `chia/wallet/puzzles/clawback/drivers.py` executes a path where make `create_merkle_proof` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/puzzles/clawback/drivers.py:88 `create_merkle_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_merkle_proof`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `create_merkle_proof` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/wallet/puzzles/clawback/drivers.py:create_merkle_proof` and assert stale pending roots die cleanly
