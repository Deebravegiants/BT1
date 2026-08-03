# Q0406: set_state partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `set_state` to fail after earlier state writes, leaving `BondedPools` or `PoolMembers` partially updated and creating a theft or freeze condition?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::set_state
- Entrypoint: signed extrinsic `set_state`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
