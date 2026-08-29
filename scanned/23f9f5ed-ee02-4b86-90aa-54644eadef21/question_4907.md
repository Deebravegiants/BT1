# Q4907: linear-interpolate via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) interpolates between two points, dividing by `(- x2 x1)`. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `collateral-receiver`, and assert the attacker's net token balance change is zero or negative.
