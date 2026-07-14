# Q2116: select_coins replays attacker-controlled spends across cache or reorg boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_coins` and control replayed bundles, reordered peer deliveries, and reorg timing so that `CATWallet.select_coins` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where use replay or rollback ordering so `select_coins` resurrects attacker-chosen spend state after it should be dead, violating the invariant that once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:479 `CATWallet.select_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_coins`
- Attacker controls: replayed bundles, reordered peer deliveries, and reorg timing
- Exploit idea: use replay or rollback ordering so `select_coins` resurrects attacker-chosen spend state after it should be dead
- Invariant to test: once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: replay the same attacker-crafted spend or wallet state across rollback/reorg test steps and assert `select_coins` never reactivates stale state
