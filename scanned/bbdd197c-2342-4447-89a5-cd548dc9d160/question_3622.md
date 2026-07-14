# Q3622: rollback accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `rollback` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `WalletPoolStore.rollback` in `chia/wallet/wallet_pool_store.py` executes a path where make `rollback` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_pool_store.py:102 `WalletPoolStore.rollback`
- Entrypoint: wallet RPC or wallet sync flow reaching `rollback`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `rollback` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/wallet_pool_store.py:rollback` and assert state changes reject cleanly
