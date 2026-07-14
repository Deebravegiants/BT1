# Q2043: set_auto_farming trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `set_auto_farming` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `SimulatorFullNodeRpcApi.set_auto_farming` in `chia/simulator/simulator_full_node_rpc_api.py` executes a path where make `set_auto_farming` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/simulator/simulator_full_node_rpc_api.py:52 `SimulatorFullNodeRpcApi.set_auto_farming`
- Entrypoint: RPC route `set_auto_farming`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `set_auto_farming` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/simulator/simulator_full_node_rpc_api.py:set_auto_farming` and assert the receiving layer revalidates every security-critical field before trusting it
