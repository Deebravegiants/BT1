# Q3070: debt-remove-scaled via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) leave a residue that no reconciliation pass ever inspects? `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
