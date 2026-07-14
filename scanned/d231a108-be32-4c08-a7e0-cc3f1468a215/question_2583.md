# Q2583: rollback_to_block evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `rollback_to_block` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `PlotNFTStore.rollback_to_block` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where cause `rollback_to_block` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:258 `PlotNFTStore.rollback_to_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `rollback_to_block`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `rollback_to_block` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/plotnft_wallet/plotnft_store.py:rollback_to_block` executes identical generator bytes on every path
