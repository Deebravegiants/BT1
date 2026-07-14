# Q1623: validate_weight_proof_inner trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_inner` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `validate_weight_proof_inner` in `chia/full_node/weight_proof.py` executes a path where make `validate_weight_proof_inner` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/weight_proof.py:1711 `validate_weight_proof_inner`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_inner`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `validate_weight_proof_inner` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/full_node/weight_proof.py:validate_weight_proof_inner` and assert the receiving layer revalidates every security-critical field before trusting it
