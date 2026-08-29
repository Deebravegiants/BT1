# Q1127: relevant via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`relevant` (mainnet/contracts/market/v0-market-vault.clar:175) drops any position row whose bit is not present in the enabled mask. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the `ft` trait principal deciding which vault is routed to, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with the `ft` trait principal deciding which vault is routed to, and assert the attacker's net token balance change is zero or negative.
