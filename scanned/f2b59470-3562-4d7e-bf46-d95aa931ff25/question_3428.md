# Q3428: new_peak_queue mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_queue` and control compact proofs, summarized state, and full-object substitution timing so that `WalletNode.new_peak_queue` in `chia/wallet/wallet_node.py` executes a path where swap compact or summarized proof material into `new_peak_queue` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:213 `WalletNode.new_peak_queue`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_queue`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `new_peak_queue` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_node.py:new_peak_queue` and assert summarized forms never bypass equivalent validation
