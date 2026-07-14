# Q2942: check_merkle_proof evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_merkle_proof` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `check_merkle_proof` in `chia/wallet/util/merkle_utils.py` executes a path where cause `check_merkle_proof` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/merkle_utils.py:101 `check_merkle_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_merkle_proof`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `check_merkle_proof` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/wallet/util/merkle_utils.py:check_merkle_proof` executes identical generator bytes on every path
