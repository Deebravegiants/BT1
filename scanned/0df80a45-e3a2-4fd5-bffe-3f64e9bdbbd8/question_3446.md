# Q3446: new_peak_from_trusted evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_from_trusted` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `WalletNode.new_peak_from_trusted` in `chia/wallet/wallet_node.py` executes a path where cause `new_peak_from_trusted` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1261 `WalletNode.new_peak_from_trusted`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_from_trusted`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_peak_from_trusted` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/wallet_node.py:new_peak_from_trusted` executes identical generator bytes on every path
