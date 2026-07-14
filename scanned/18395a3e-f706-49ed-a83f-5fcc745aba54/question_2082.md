# Q2082: request_compact_proof_of_time cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach P2P message handler `request_compact_proof_of_time` and control batched updates across multiple store ids and roots so that `TimelordAPI.request_compact_proof_of_time` in `chia/timelord/timelord_api.py` executes a path where make `request_compact_proof_of_time` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/timelord/timelord_api.py:203 `TimelordAPI.request_compact_proof_of_time`
- Entrypoint: P2P message handler `request_compact_proof_of_time`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `request_compact_proof_of_time` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/timelord/timelord_api.py:request_compact_proof_of_time` and assert no store commits under the wrong root
