# Q183: start_plotting trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `start_plotting` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WebSocketServer.start_plotting` in `chia/daemon/server.py` executes a path where make `start_plotting` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/daemon/server.py:1158 `WebSocketServer.start_plotting`
- Entrypoint: daemon WebSocket command path reaching `start_plotting`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `start_plotting` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/daemon/server.py:start_plotting` and assert the receiving layer revalidates every security-critical field before trusting it
