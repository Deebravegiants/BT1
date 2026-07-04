# Q1091: Pool certificate ordering can create inconsistent pool or reward state in dState'

## Question
Can an unprivileged attacker exercise `dState'` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs` via the stated entrypoint and trigger pool registration retirement ordering mismatch? The investigation should test whether pool state and delegation/reward state update in different orders, leaving stake delegated to a removed pool or rewards assigned to an impossible credential.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs / dState'
- Entrypoint: Submit transactions and epoch-boundary sequences with pool registration, retirement, delegation, deregistration, and reward withdrawal edge cases.
- Attacker controls: Pool certificates, stake credentials, delegation certificates, pool metadata, retirement epoch, reward accounts, and ordering across transactions.
- Exploit idea: Check whether pool state and delegation/reward state update in different orders, leaving stake delegated to a removed pool or rewards assigned to an impossible credential.
- Invariant to test: State-transition invariant: certificates, delegation, staking, rewards, pools, UTxO, and account state must update atomically and match the final obligation/deposit/reward state.
- Expected Cardano/Intersect impact: Potential Medium if an unprivileged user can trigger incorrect fees, deposits, refunds, rewards, withdrawals, treasury movement, or validation limits without full chain split.
- Fast validation: Build a minimal sequence of transactions or certificates around the boundary condition and assert deposits, refunds, withdrawals, and UTxO state after each step.
