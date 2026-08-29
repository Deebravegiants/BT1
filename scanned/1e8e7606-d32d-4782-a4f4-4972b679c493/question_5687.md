# Q5687: resolve-interpolation-points via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
`resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) selects the bracketing curve points for a utilization. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the trait principals supplied per entry, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with the trait principals supplied per entry, and assert the attacker's net token balance change is zero or negative.
