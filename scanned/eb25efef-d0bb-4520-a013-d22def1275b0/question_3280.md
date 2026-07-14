# Q3280: set_peak_block evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_peak_block` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `WalletBlockchain.set_peak_block` in `chia/wallet/wallet_blockchain.py` executes a path where cause `set_peak_block` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_blockchain.py:179 `WalletBlockchain.set_peak_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_peak_block`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `set_peak_block` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/wallet_blockchain.py:set_peak_block` executes identical generator bytes on every path
