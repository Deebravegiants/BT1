# Q3445: new_peak_from_trusted reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_from_trusted` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `WalletNode.new_peak_from_trusted` in `chia/wallet/wallet_node.py` executes a path where reuse cache, dedup, or seen-set assumptions in `new_peak_from_trusted` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1261 `WalletNode.new_peak_from_trusted`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_from_trusted`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `new_peak_from_trusted` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/wallet/wallet_node.py:new_peak_from_trusted` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
