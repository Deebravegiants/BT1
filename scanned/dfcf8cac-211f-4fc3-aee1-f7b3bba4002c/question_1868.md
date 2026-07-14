# Q1868: generate_signed_transaction applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_signed_transaction` and control public RPC or WebSocket command arguments that select protected actions so that `PoolWallet.generate_signed_transaction` in `chia/pools/pool_wallet.py` executes a path where reach a privileged path in `generate_signed_transaction` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_wallet.py:899 `PoolWallet.generate_signed_transaction`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_signed_transaction`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `generate_signed_transaction` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/pools/pool_wallet.py:generate_signed_transaction` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
