# Q1626: new_signage_point_harvester reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_harvester` and control one request's authorization context plus a second request that reuses cached state so that `HarvesterAPI.new_signage_point_harvester` in `chia/harvester/harvester_api.py` executes a path where make `new_signage_point_harvester` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/harvester/harvester_api.py:130 `HarvesterAPI.new_signage_point_harvester`
- Entrypoint: P2P message handler `new_signage_point_harvester`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `new_signage_point_harvester` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/harvester/harvester_api.py:new_signage_point_harvester` with different identities and assert auth state cannot bleed across them
