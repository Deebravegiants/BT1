# Q1096: new_end_of_sub_slot_vdf evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach P2P message handler `new_end_of_sub_slot_vdf` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `FullNodeAPI.new_end_of_sub_slot_vdf` in `chia/full_node/full_node_api.py` executes a path where cause `new_end_of_sub_slot_vdf` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:1317 `FullNodeAPI.new_end_of_sub_slot_vdf`
- Entrypoint: P2P message handler `new_end_of_sub_slot_vdf`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_end_of_sub_slot_vdf` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/full_node/full_node_api.py:new_end_of_sub_slot_vdf` executes identical generator bytes on every path
