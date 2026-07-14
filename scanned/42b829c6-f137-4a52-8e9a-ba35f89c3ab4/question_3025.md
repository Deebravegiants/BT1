# Q3025: request_header_blocks trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `request_header_blocks` and control block, header, proof, or weight fields supplied over the peer protocol so that `request_header_blocks` in `chia/wallet/util/wallet_sync_utils.py` executes a path where make `request_header_blocks` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:248 `request_header_blocks`
- Entrypoint: wallet RPC or wallet sync flow reaching `request_header_blocks`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `request_header_blocks` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/wallet/util/wallet_sync_utils.py:request_header_blocks` and assert both derive the same rejection
