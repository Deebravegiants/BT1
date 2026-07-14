# Q1835: new_peak accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `new_peak` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PoolWallet.new_peak` in `chia/pools/pool_wallet.py` executes a path where make `new_peak` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:807 `PoolWallet.new_peak`
- Entrypoint: pool wallet or singleton spend flow reaching `new_peak`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `new_peak` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/pools/pool_wallet.py:new_peak` and assert state changes reject cleanly
