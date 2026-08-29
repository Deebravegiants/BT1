# Q1835: vault-accrue via redeem: leave a residue that no reconciliation pass ever inspects

## Question
`vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) dispatches accrual to one of six vaults by asset id. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `amount` of shares burned, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with `amount` of shares burned, and assert the attacker's net token balance change is zero or negative.
