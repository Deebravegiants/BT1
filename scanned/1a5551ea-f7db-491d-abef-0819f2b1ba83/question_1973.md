# Q1973: request_signage_point_or_end_of_sub_slot applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach P2P message handler `request_signage_point_or_end_of_sub_slot` and control public RPC or WebSocket command arguments that select protected actions so that `CrawlerAPI.request_signage_point_or_end_of_sub_slot` in `chia/seeder/crawler_api.py` executes a path where reach a privileged path in `request_signage_point_or_end_of_sub_slot` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/seeder/crawler_api.py:98 `CrawlerAPI.request_signage_point_or_end_of_sub_slot`
- Entrypoint: P2P message handler `request_signage_point_or_end_of_sub_slot`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `request_signage_point_or_end_of_sub_slot` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/seeder/crawler_api.py:request_signage_point_or_end_of_sub_slot` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
