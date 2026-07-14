# Q577: new_proof_of_space cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach P2P message handler `new_proof_of_space` and control batched updates across multiple store ids and roots so that `FarmerAPI.new_proof_of_space` in `chia/farmer/farmer_api.py` executes a path where make `new_proof_of_space` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/farmer/farmer_api.py:72 `FarmerAPI.new_proof_of_space`
- Entrypoint: P2P message handler `new_proof_of_space`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `new_proof_of_space` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/farmer/farmer_api.py:new_proof_of_space` and assert no store commits under the wrong root
