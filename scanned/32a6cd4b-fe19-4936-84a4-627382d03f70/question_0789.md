# Q789: add_transaction_semaphore replays attacker-controlled spends across cache or reorg boundaries

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_transaction_semaphore` and control replayed bundles, reordered peer deliveries, and reorg timing so that `FullNode.add_transaction_semaphore` in `chia/full_node/full_node.py` executes a path where use replay or rollback ordering so `add_transaction_semaphore` resurrects attacker-chosen spend state after it should be dead, violating the invariant that once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:459 `FullNode.add_transaction_semaphore`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_transaction_semaphore`
- Attacker controls: replayed bundles, reordered peer deliveries, and reorg timing
- Exploit idea: use replay or rollback ordering so `add_transaction_semaphore` resurrects attacker-chosen spend state after it should be dead
- Invariant to test: once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: replay the same attacker-crafted spend or wallet state across rollback/reorg test steps and assert `add_transaction_semaphore` never reactivates stale state
