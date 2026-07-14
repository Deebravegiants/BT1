# Q3004: add_to_additions_in_block replays stale sync messages into live state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_additions_in_block` and control stale but protocol-valid sync messages replayed after newer state is present so that `PeerRequestCache.add_to_additions_in_block` in `chia/wallet/util/peer_request_cache.py` executes a path where replay stale sync objects into `add_to_additions_in_block` after newer canonical state is known and see if they still mutate storage, violating the invariant that stale sync messages must become inert once newer canonical state supersedes them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:88 `PeerRequestCache.add_to_additions_in_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_additions_in_block`
- Attacker controls: stale but protocol-valid sync messages replayed after newer state is present
- Exploit idea: replay stale sync objects into `add_to_additions_in_block` after newer canonical state is known and see if they still mutate storage
- Invariant to test: stale sync messages must become inert once newer canonical state supersedes them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale sync messages after newer ones into `chia/wallet/util/peer_request_cache.py:add_to_additions_in_block` and assert they cannot mutate final stored state
