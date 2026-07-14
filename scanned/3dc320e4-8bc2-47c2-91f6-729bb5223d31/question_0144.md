# Q144: setup_process_global_state trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `setup_process_global_state` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `WebSocketServer.setup_process_global_state` in `chia/daemon/server.py` executes a path where make `setup_process_global_state` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/daemon/server.py:245 `WebSocketServer.setup_process_global_state`
- Entrypoint: daemon WebSocket command path reaching `setup_process_global_state`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `setup_process_global_state` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/daemon/server.py:setup_process_global_state` and assert the receiving layer revalidates every security-critical field before trusting it
