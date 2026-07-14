# Q1715: create_pooling_inner_puzzle replays attacker-controlled spends across cache or reorg boundaries

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_pooling_inner_puzzle` and control replayed bundles, reordered peer deliveries, and reorg timing so that `create_pooling_inner_puzzle` in `chia/pools/pool_puzzles.py` executes a path where use replay or rollback ordering so `create_pooling_inner_puzzle` resurrects attacker-chosen spend state after it should be dead, violating the invariant that once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_puzzles.py:67 `create_pooling_inner_puzzle`
- Entrypoint: pool wallet or singleton spend flow reaching `create_pooling_inner_puzzle`
- Attacker controls: replayed bundles, reordered peer deliveries, and reorg timing
- Exploit idea: use replay or rollback ordering so `create_pooling_inner_puzzle` resurrects attacker-chosen spend state after it should be dead
- Invariant to test: once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: replay the same attacker-crafted spend or wallet state across rollback/reorg test steps and assert `create_pooling_inner_puzzle` never reactivates stale state
