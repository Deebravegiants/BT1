# Q5555: add-user-collateral via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
`add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) adds to the collateral row with a graceful u0 default. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing whether the position has any enabled debt row (the has-debt branch), use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with whether the position has any enabled debt row (the has-debt branch), and assert the attacker's net token balance change is zero or negative.
