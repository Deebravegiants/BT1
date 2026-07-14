# Q2959: subscribe_to_coin_ids replays stale sync messages into live state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids` and control stale but protocol-valid sync messages replayed after newer state is present so that `NewPeakQueue.subscribe_to_coin_ids` in `chia/wallet/util/new_peak_queue.py` executes a path where replay stale sync objects into `subscribe_to_coin_ids` after newer canonical state is known and see if they still mutate storage, violating the invariant that stale sync messages must become inert once newer canonical state supersedes them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:61 `NewPeakQueue.subscribe_to_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids`
- Attacker controls: stale but protocol-valid sync messages replayed after newer state is present
- Exploit idea: replay stale sync objects into `subscribe_to_coin_ids` after newer canonical state is known and see if they still mutate storage
- Invariant to test: stale sync messages must become inert once newer canonical state supersedes them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale sync messages after newer ones into `chia/wallet/util/new_peak_queue.py:subscribe_to_coin_ids` and assert they cannot mutate final stored state
