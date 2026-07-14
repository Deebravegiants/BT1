# Q652: set_payout_instructions trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach RPC route `set_payout_instructions` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `FarmerRpcApi.set_payout_instructions` in `chia/farmer/farmer_rpc_api.py` executes a path where make `set_payout_instructions` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:317 `FarmerRpcApi.set_payout_instructions`
- Entrypoint: RPC route `set_payout_instructions`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `set_payout_instructions` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/farmer/farmer_rpc_api.py:set_payout_instructions` and assert the receiving layer revalidates every security-critical field before trusting it
