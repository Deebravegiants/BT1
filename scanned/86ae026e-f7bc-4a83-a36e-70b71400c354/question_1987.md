# Q1987: request_mempool_transactions accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach P2P message handler `request_mempool_transactions` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `CrawlerAPI.request_mempool_transactions` in `chia/seeder/crawler_api.py` executes a path where make `request_mempool_transactions` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/seeder/crawler_api.py:104 `CrawlerAPI.request_mempool_transactions`
- Entrypoint: P2P message handler `request_mempool_transactions`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `request_mempool_transactions` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/seeder/crawler_api.py:request_mempool_transactions` and assert state changes reject cleanly
