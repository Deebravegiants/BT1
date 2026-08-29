# Q3670: socialize-debt via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `socialize-debt` (mainnet/contracts/vault/v0-vault-stx.clar:944) leave a residue that no reconciliation pass ever inspects? `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:944` -> `socialize-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
