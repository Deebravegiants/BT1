# Q3468: sync_from_untrusted_close_to_peak mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak` and control compact proofs, summarized state, and full-object substitution timing so that `WalletNode.sync_from_untrusted_close_to_peak` in `chia/wallet/wallet_node.py` executes a path where swap compact or summarized proof material into `sync_from_untrusted_close_to_peak` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1339 `WalletNode.sync_from_untrusted_close_to_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `sync_from_untrusted_close_to_peak` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_node.py:sync_from_untrusted_close_to_peak` and assert summarized forms never bypass equivalent validation
