# Q2986: add_to_block_signatures_validated trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated` and control block, header, proof, or weight fields supplied over the peer protocol so that `PeerRequestCache.add_to_block_signatures_validated` in `chia/wallet/util/peer_request_cache.py` executes a path where make `add_to_block_signatures_validated` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:72 `PeerRequestCache.add_to_block_signatures_validated`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `add_to_block_signatures_validated` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/wallet/util/peer_request_cache.py:add_to_block_signatures_validated` and assert both derive the same rejection
