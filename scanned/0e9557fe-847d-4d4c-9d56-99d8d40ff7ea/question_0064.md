# Q64: add_block_record evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_record` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `Blockchain.add_block_record` in `chia/consensus/blockchain.py` executes a path where cause `add_block_record` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain.py:1011 `Blockchain.add_block_record`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_record`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `add_block_record` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/consensus/blockchain.py:add_block_record` executes identical generator bytes on every path
