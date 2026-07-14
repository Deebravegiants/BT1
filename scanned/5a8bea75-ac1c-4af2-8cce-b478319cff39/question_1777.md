# Q1777: create_absorb_spend accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_absorb_spend` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `create_absorb_spend` in `chia/pools/pool_puzzles.py` executes a path where make `create_absorb_spend` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_puzzles.py:252 `create_absorb_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `create_absorb_spend`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `create_absorb_spend` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/pools/pool_puzzles.py:create_absorb_spend` and assert state changes reject cleanly
