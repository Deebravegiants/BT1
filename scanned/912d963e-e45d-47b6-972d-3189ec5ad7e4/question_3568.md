# Q3568: respond_block_headers mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach P2P message handler `respond_block_headers` and control compact proofs, summarized state, and full-object substitution timing so that `WalletNodeAPI.respond_block_headers` in `chia/wallet/wallet_node_api.py` executes a path where swap compact or summarized proof material into `respond_block_headers` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node_api.py:181 `WalletNodeAPI.respond_block_headers`
- Entrypoint: P2P message handler `respond_block_headers`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `respond_block_headers` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/wallet_node_api.py:respond_block_headers` and assert summarized forms never bypass equivalent validation
