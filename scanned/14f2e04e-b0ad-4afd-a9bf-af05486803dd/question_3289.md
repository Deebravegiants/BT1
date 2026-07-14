# Q3289: set_finished_sync_up_to replays stale sync messages into live state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_finished_sync_up_to` and control stale but protocol-valid sync messages replayed after newer state is present so that `WalletBlockchain.set_finished_sync_up_to` in `chia/wallet/wallet_blockchain.py` executes a path where replay stale sync objects into `set_finished_sync_up_to` after newer canonical state is known and see if they still mutate storage, violating the invariant that stale sync messages must become inert once newer canonical state supersedes them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:197 `WalletBlockchain.set_finished_sync_up_to`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_finished_sync_up_to`
- Attacker controls: stale but protocol-valid sync messages replayed after newer state is present
- Exploit idea: replay stale sync objects into `set_finished_sync_up_to` after newer canonical state is known and see if they still mutate storage
- Invariant to test: stale sync messages must become inert once newer canonical state supersedes them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale sync messages after newer ones into `chia/wallet/wallet_blockchain.py:set_finished_sync_up_to` and assert they cannot mutate final stored state
