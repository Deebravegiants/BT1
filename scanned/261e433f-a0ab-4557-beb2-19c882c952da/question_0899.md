# Q899: add_to_bad_peak_cache evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `FullNode.add_to_bad_peak_cache` in `chia/full_node/full_node.py` executes a path where cause `add_to_bad_peak_cache` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3357 `FullNode.add_to_bad_peak_cache`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `add_to_bad_peak_cache` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/full_node/full_node.py:add_to_bad_peak_cache` executes identical generator bytes on every path
