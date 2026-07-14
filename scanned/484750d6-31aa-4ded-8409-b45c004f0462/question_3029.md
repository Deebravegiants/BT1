# Q3029: request_header_blocks derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `request_header_blocks` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `request_header_blocks` in `chia/wallet/util/wallet_sync_utils.py` executes a path where make `request_header_blocks` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:248 `request_header_blocks`
- Entrypoint: wallet RPC or wallet sync flow reaching `request_header_blocks`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `request_header_blocks` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/wallet/util/wallet_sync_utils.py:request_header_blocks` and assert fork choice depends only on canonical validated state
