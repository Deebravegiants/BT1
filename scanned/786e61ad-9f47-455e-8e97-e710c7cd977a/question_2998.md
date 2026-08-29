# Q2998: insert via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `borrower`, any third-party principal, can an unprivileged attacker make `insert` (mainnet/contracts/market/v0-market-vault.clar:159) leave a residue that no reconciliation pass ever inspects? `insert` rewrites the whole registry entry for a user id, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with `borrower`, any third-party principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
