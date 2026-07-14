# Q1974: request_signage_point_or_end_of_sub_slot reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `request_signage_point_or_end_of_sub_slot` and control one request's authorization context plus a second request that reuses cached state so that `CrawlerAPI.request_signage_point_or_end_of_sub_slot` in `chia/seeder/crawler_api.py` executes a path where make `request_signage_point_or_end_of_sub_slot` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/seeder/crawler_api.py:98 `CrawlerAPI.request_signage_point_or_end_of_sub_slot`
- Entrypoint: P2P message handler `request_signage_point_or_end_of_sub_slot`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `request_signage_point_or_end_of_sub_slot` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/seeder/crawler_api.py:request_signage_point_or_end_of_sub_slot` with different identities and assert auth state cannot bleed across them
