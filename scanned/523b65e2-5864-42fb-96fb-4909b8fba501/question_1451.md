# Q1451: vault-accrue via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) dispatches accrual to one of six vaults by asset id. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing call ordering within the block, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with call ordering within the block, and assert the attacker's net token balance change is zero or negative.
