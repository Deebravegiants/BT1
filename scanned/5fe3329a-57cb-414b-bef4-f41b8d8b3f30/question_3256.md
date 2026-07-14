# Q3256: new_valid_weight_proof evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_valid_weight_proof` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `WalletBlockchain.new_valid_weight_proof` in `chia/wallet/wallet_blockchain.py` executes a path where cause `new_valid_weight_proof` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_blockchain.py:81 `WalletBlockchain.new_valid_weight_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_valid_weight_proof`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_valid_weight_proof` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/wallet_blockchain.py:new_valid_weight_proof` executes identical generator bytes on every path
