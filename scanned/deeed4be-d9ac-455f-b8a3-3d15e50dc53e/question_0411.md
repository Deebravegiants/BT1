# Q0411: redeem partial failure can leave ghost accounting

## Question
Can an unprivileged attacker force `redeem` to fail after earlier state writes, leaving `PsmInfos` or `PsmDebt` partially updated and creating a theft or freeze condition?

## Target
- File/function: substrate/frame/psm/src/lib.rs::redeem
- Entrypoint: signed extrinsic `redeem`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Target the latest possible failing branch after balances, deposits, or ownership state has already moved.
- Invariant to test: All touched storage must roll back atomically; no ghost holds, deposits, liabilities, or ownership edges may survive an error.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Use adversarial parameters plus nested batch execution and compare pre/post storage snapshots.
