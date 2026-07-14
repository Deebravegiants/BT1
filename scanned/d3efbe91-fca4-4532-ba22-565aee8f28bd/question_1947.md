# Q1947: request_proof_of_weight cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control batched updates across multiple store ids and roots so that `CrawlerAPI.request_proof_of_weight` in `chia/seeder/crawler_api.py` executes a path where make `request_proof_of_weight` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/seeder/crawler_api.py:80 `CrawlerAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `request_proof_of_weight` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/seeder/crawler_api.py:request_proof_of_weight` and assert no store commits under the wrong root
