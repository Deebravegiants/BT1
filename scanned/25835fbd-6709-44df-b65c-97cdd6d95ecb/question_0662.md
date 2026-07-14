# Q662: new_block_height mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_block_height` and control compact proofs, summarized state, and full-object substitution timing so that `BitcoinFeeEstimator.new_block_height` in `chia/full_node/bitcoin_fee_estimator.py` executes a path where swap compact or summarized proof material into `new_block_height` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/bitcoin_fee_estimator.py:31 `BitcoinFeeEstimator.new_block_height`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_block_height`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `new_block_height` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/bitcoin_fee_estimator.py:new_block_height` and assert summarized forms never bypass equivalent validation
