# Q0329: burn partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `burn` to fail after earlier state writes, leaving `AssetDetails` or `Accounts` partially updated and creating a theft or freeze condition?

## Target
- File/function: substrate/frame/assets/src/lib.rs::burn
- Entrypoint: signed extrinsic `burn`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
