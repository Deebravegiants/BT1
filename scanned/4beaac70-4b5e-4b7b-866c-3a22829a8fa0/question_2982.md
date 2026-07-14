# Q2982: add_to_block_requests evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_requests` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `PeerRequestCache.add_to_block_requests` in `chia/wallet/util/peer_request_cache.py` executes a path where cause `add_to_block_requests` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:49 `PeerRequestCache.add_to_block_requests`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_requests`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `add_to_block_requests` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/util/peer_request_cache.py:add_to_block_requests` executes identical generator bytes on every path
