# Q1831: new_peak evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `new_peak` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `PoolWallet.new_peak` in `chia/pools/pool_wallet.py` executes a path where cause `new_peak` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_wallet.py:807 `PoolWallet.new_peak`
- Entrypoint: pool wallet or singleton spend flow reaching `new_peak`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_peak` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/pools/pool_wallet.py:new_peak` executes identical generator bytes on every path
