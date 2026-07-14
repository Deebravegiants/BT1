# Q718: new_block evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_block` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `CoinStore.new_block` in `chia/full_node/coin_store.py` executes a path where cause `new_block` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/coin_store.py:105 `CoinStore.new_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_block`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_block` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/full_node/coin_store.py:new_block` executes identical generator bytes on every path
