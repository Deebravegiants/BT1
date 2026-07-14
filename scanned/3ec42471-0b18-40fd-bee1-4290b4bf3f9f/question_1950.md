# Q1950: request_proof_of_weight trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `CrawlerAPI.request_proof_of_weight` in `chia/seeder/crawler_api.py` executes a path where make `request_proof_of_weight` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/seeder/crawler_api.py:80 `CrawlerAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `request_proof_of_weight` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/seeder/crawler_api.py:request_proof_of_weight` and assert the receiving layer revalidates every security-critical field before trusting it
