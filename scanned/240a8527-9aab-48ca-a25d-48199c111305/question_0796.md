# Q796: new_peak_sem trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_peak_sem` and control block, header, proof, or weight fields supplied over the peer protocol so that `FullNode.new_peak_sem` in `chia/full_node/full_node.py` executes a path where make `new_peak_sem` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:479 `FullNode.new_peak_sem`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_peak_sem`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `new_peak_sem` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/full_node/full_node.py:new_peak_sem` and assert both derive the same rejection
