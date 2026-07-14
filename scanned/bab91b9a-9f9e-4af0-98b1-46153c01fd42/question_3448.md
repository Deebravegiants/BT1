# Q3448: new_peak_from_trusted mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_from_trusted` and control compact proofs, summarized state, and full-object substitution timing so that `WalletNode.new_peak_from_trusted` in `chia/wallet/wallet_node.py` executes a path where swap compact or summarized proof material into `new_peak_from_trusted` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1261 `WalletNode.new_peak_from_trusted`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_from_trusted`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `new_peak_from_trusted` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_node.py:new_peak_from_trusted` and assert summarized forms never bypass equivalent validation
