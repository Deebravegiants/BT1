# Q3618: add_spend accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_spend` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `WalletPoolStore.add_spend` in `chia/wallet/wallet_pool_store.py` executes a path where make `add_spend` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_pool_store.py:33 `WalletPoolStore.add_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_spend`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `add_spend` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/wallet_pool_store.py:add_spend` and assert state changes reject cleanly
