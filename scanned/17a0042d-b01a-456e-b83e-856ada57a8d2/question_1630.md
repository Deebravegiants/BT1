# Q1630: new_signage_point_harvester trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_harvester` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `HarvesterAPI.new_signage_point_harvester` in `chia/harvester/harvester_api.py` executes a path where make `new_signage_point_harvester` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/harvester/harvester_api.py:130 `HarvesterAPI.new_signage_point_harvester`
- Entrypoint: P2P message handler `new_signage_point_harvester`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `new_signage_point_harvester` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/harvester/harvester_api.py:new_signage_point_harvester` and assert the receiving layer revalidates every security-critical field before trusting it
