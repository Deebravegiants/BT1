# Q2590: rollback_to_block accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `rollback_to_block` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PlotNFTStore.rollback_to_block` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `rollback_to_block` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:258 `PlotNFTStore.rollback_to_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `rollback_to_block`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `rollback_to_block` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/wallet/plotnft_wallet/plotnft_store.py:rollback_to_block` and assert state changes reject cleanly
