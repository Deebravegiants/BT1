# Q644: get_signage_points trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `get_signage_points` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `FarmerRpcApi.get_signage_points` in `chia/farmer/farmer_rpc_api.py` executes a path where make `get_signage_points` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:266 `FarmerRpcApi.get_signage_points`
- Entrypoint: RPC route `get_signage_points`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `get_signage_points` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/farmer/farmer_rpc_api.py:get_signage_points` and assert the receiving layer revalidates every security-critical field before trusting it
