# Q2473: update_coin_status replays attacker-controlled spends across cache or reorg boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_coin_status` and control replayed bundles, reordered peer deliveries, and reorg timing so that `NFTWallet.update_coin_status` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where use replay or rollback ordering so `update_coin_status` resurrects attacker-chosen spend state after it should be dead, violating the invariant that once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:482 `NFTWallet.update_coin_status`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_coin_status`
- Attacker controls: replayed bundles, reordered peer deliveries, and reorg timing
- Exploit idea: use replay or rollback ordering so `update_coin_status` resurrects attacker-chosen spend state after it should be dead
- Invariant to test: once a spend path is invalidated by confirmation, rollback, or conflict resolution, it must not silently become active again
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: replay the same attacker-crafted spend or wallet state across rollback/reorg test steps and assert `update_coin_status` never reactivates stale state
