# Q1675: claim_pool_reward_dpuz_and_solution carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_reward_dpuz_and_solution` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `PlotNFTPuzzle.claim_pool_reward_dpuz_and_solution` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_reward_dpuz_and_solution` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/plotnft_drivers.py:162 `PlotNFTPuzzle.claim_pool_reward_dpuz_and_solution`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_reward_dpuz_and_solution`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `claim_pool_reward_dpuz_and_solution` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/pools/plotnft_drivers.py:claim_pool_reward_dpuz_and_solution` and assert stale spend state is purged before replayed data is reconsidered
