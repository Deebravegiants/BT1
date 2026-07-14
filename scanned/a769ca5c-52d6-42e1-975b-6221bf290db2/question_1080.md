# Q1080: new_signage_point_vdf trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_vdf` and control block, header, proof, or weight fields supplied over the peer protocol so that `FullNodeAPI.new_signage_point_vdf` in `chia/full_node/full_node_api.py` executes a path where make `new_signage_point_vdf` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:1301 `FullNodeAPI.new_signage_point_vdf`
- Entrypoint: P2P message handler `new_signage_point_vdf`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `new_signage_point_vdf` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/full_node/full_node_api.py:new_signage_point_vdf` and assert both derive the same rejection
