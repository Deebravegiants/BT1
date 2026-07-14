# Q2045: new_peak_timelord trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_timelord` and control block, header, proof, or weight fields supplied over the peer protocol so that `TimelordAPI.new_peak_timelord` in `chia/timelord/timelord_api.py` executes a path where make `new_peak_timelord` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/timelord/timelord_api.py:60 `TimelordAPI.new_peak_timelord`
- Entrypoint: P2P message handler `new_peak_timelord`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `new_peak_timelord` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/timelord/timelord_api.py:new_peak_timelord` and assert both derive the same rejection
