# Q0412: add_tip partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `add_tip` to fail after earlier state writes, leaving `ForeignToNativeId` or `LostTips` partially updated and creating a theft or freeze condition?

## Target
- File/function: bridges/snowbridge/pallets/system-frontend/src/lib.rs::add_tip
- Entrypoint: signed extrinsic `add_tip`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
