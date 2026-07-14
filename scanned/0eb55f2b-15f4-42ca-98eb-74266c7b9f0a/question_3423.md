# Q3423: new_peak_queue trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_queue` and control block, header, proof, or weight fields supplied over the peer protocol so that `WalletNode.new_peak_queue` in `chia/wallet/wallet_node.py` executes a path where make `new_peak_queue` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:213 `WalletNode.new_peak_queue`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_queue`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `new_peak_queue` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/wallet/wallet_node.py:new_peak_queue` and assert both derive the same rejection
