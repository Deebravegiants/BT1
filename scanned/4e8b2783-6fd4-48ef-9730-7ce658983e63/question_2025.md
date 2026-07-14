# Q2025: connection_closed trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach inbound peer connection path reaching `connection_closed` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `ChiaServer.connection_closed` in `chia/server/server.py` executes a path where make `connection_closed` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/server/server.py:599 `ChiaServer.connection_closed`
- Entrypoint: inbound peer connection path reaching `connection_closed`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `connection_closed` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/server/server.py:connection_closed` and assert the receiving layer revalidates every security-critical field before trusting it
