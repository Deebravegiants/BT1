# Q597: partial_proofs trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach P2P message handler `partial_proofs` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `FarmerAPI.partial_proofs` in `chia/farmer/farmer_api.py` executes a path where make `partial_proofs` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/farmer/farmer_api.py:495 `FarmerAPI.partial_proofs`
- Entrypoint: P2P message handler `partial_proofs`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `partial_proofs` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/farmer/farmer_api.py:partial_proofs` and assert the receiving layer revalidates every security-critical field before trusting it
