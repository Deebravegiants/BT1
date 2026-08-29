# Q3550: refresh via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) leave a residue that no reconciliation pass ever inspects? `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
