# Q3058: system-repay via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `borrower`, any third-party principal, can an unprivileged attacker make `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) leave a residue that no reconciliation pass ever inspects? `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate` with `borrower`, any third-party principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
