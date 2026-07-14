# Q2232: create_graftroot_offer_puz reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_graftroot_offer_puz` and control pending roots, clear/cancel timing, and subsequent root submissions so that `create_graftroot_offer_puz` in `chia/wallet/db_wallet/db_wallet_puzzles.py` executes a path where make `create_graftroot_offer_puz` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/db_wallet/db_wallet_puzzles.py:79 `create_graftroot_offer_puz`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_graftroot_offer_puz`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `create_graftroot_offer_puz` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/wallet/db_wallet/db_wallet_puzzles.py:create_graftroot_offer_puz` and assert stale pending roots die cleanly
