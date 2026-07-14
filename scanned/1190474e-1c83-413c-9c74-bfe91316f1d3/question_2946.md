# Q2946: check_merkle_proof cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_merkle_proof` and control batched updates across multiple store ids and roots so that `check_merkle_proof` in `chia/wallet/util/merkle_utils.py` executes a path where make `check_merkle_proof` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/merkle_utils.py:101 `check_merkle_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_merkle_proof`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `check_merkle_proof` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/wallet/util/merkle_utils.py:check_merkle_proof` and assert no store commits under the wrong root
