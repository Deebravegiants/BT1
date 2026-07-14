# Q3467: sync_from_untrusted_close_to_peak derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `WalletNode.sync_from_untrusted_close_to_peak` in `chia/wallet/wallet_node.py` executes a path where make `sync_from_untrusted_close_to_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1339 `WalletNode.sync_from_untrusted_close_to_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `sync_from_untrusted_close_to_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/wallet/wallet_node.py:sync_from_untrusted_close_to_peak` and assert fork choice depends only on canonical validated state
