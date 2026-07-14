# Q2977: new_peak_wallet mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_wallet` and control compact proofs, summarized state, and full-object substitution timing so that `NewPeakQueue.new_peak_wallet` in `chia/wallet/util/new_peak_queue.py` executes a path where swap compact or summarized proof material into `new_peak_wallet` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:73 `NewPeakQueue.new_peak_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_wallet`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `new_peak_wallet` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/util/new_peak_queue.py:new_peak_wallet` and assert summarized forms never bypass equivalent validation
