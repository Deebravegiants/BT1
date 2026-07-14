# Q2032: set_capabilities trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach inbound peer connection path reaching `set_capabilities` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `ChiaServer.set_capabilities` in `chia/server/server.py` executes a path where make `set_capabilities` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/server/server.py:810 `ChiaServer.set_capabilities`
- Entrypoint: inbound peer connection path reaching `set_capabilities`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `set_capabilities` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/server/server.py:set_capabilities` and assert the receiving layer revalidates every security-critical field before trusting it
