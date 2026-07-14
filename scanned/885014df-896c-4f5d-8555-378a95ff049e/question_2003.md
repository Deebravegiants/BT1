# Q2003: request_removals replays stale sync messages into live state

## Question
Can an unprivileged attacker reach P2P message handler `request_removals` and control stale but protocol-valid sync messages replayed after newer state is present so that `CrawlerAPI.request_removals` in `chia/seeder/crawler_api.py` executes a path where replay stale sync objects into `request_removals` after newer canonical state is known and see if they still mutate storage, violating the invariant that stale sync messages must become inert once newer canonical state supersedes them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/seeder/crawler_api.py:120 `CrawlerAPI.request_removals`
- Entrypoint: P2P message handler `request_removals`
- Attacker controls: stale but protocol-valid sync messages replayed after newer state is present
- Exploit idea: replay stale sync objects into `request_removals` after newer canonical state is known and see if they still mutate storage
- Invariant to test: stale sync messages must become inert once newer canonical state supersedes them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale sync messages after newer ones into `chia/seeder/crawler_api.py:request_removals` and assert they cannot mutate final stored state
