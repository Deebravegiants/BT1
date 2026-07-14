# Q2984: add_to_block_requests mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_requests` and control compact proofs, summarized state, and full-object substitution timing so that `PeerRequestCache.add_to_block_requests` in `chia/wallet/util/peer_request_cache.py` executes a path where swap compact or summarized proof material into `add_to_block_requests` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:49 `PeerRequestCache.add_to_block_requests`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_requests`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `add_to_block_requests` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/util/peer_request_cache.py:add_to_block_requests` and assert summarized forms never bypass equivalent validation
