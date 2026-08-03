# Q0389: bond_extra partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `bond_extra` to fail after earlier state writes, leaving `BondedPools` or `PoolMembers` partially updated and creating a theft or freeze condition?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::bond_extra
- Entrypoint: signed extrinsic `bond_extra`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
