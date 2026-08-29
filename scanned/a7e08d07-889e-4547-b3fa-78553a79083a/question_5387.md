# Q5387: calc-index-next via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
`calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) applies a multiplier to the current index. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `min-shares` (the only slippage bound on the deposit leg), use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with `min-shares` (the only slippage bound on the deposit leg), and assert the attacker's net token balance change is zero or negative.
