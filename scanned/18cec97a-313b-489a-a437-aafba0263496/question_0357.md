# Q0357: create_swap partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `create_swap` to fail after earlier state writes, leaving `PendingSwaps` or `hashlock state` partially updated and creating a theft or freeze condition?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::create_swap
- Entrypoint: signed extrinsic `create_swap`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
