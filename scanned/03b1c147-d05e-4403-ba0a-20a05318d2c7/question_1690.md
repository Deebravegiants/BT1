# Q1690: claim_pool_rewards accepts a pool membership transition with stale or swapped state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_rewards` and control launcher ids, pool target state, delayed puzzle data, and join/leave sequencing so that `PlotNFT.claim_pool_rewards` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_rewards` apply pool join, leave, or waiting-room state under swapped singleton context, violating the invariant that pool membership state must advance only through canonical singleton transitions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/plotnft_drivers.py:589 `PlotNFT.claim_pool_rewards`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_rewards`
- Attacker controls: launcher ids, pool target state, delayed puzzle data, and join/leave sequencing
- Exploit idea: make `claim_pool_rewards` apply pool join, leave, or waiting-room state under swapped singleton context
- Invariant to test: pool membership state must advance only through canonical singleton transitions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: drive join/leave transitions with stale singleton context into `chia/pools/plotnft_drivers.py:claim_pool_rewards` and assert state changes reject cleanly
