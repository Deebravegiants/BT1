# Q3282: set_peak_block mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_peak_block` and control compact proofs, summarized state, and full-object substitution timing so that `WalletBlockchain.set_peak_block` in `chia/wallet/wallet_blockchain.py` executes a path where swap compact or summarized proof material into `set_peak_block` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_blockchain.py:179 `WalletBlockchain.set_peak_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_peak_block`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `set_peak_block` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_blockchain.py:set_peak_block` and assert summarized forms never bypass equivalent validation
