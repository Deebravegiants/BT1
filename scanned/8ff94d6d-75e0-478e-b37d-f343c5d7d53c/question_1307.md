# Q1307: calc-index-next via borrow: leave a residue that no reconciliation pass ever inspects

## Question
`calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) applies a multiplier to the current index. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the order of accrual versus price resolution inside the let, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the order of accrual versus price resolution inside the let, and assert the attacker's net token balance change is zero or negative.
