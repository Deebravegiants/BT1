# Q0718: get-cached-indexes via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) mint shares whose backing was never received? `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `deposit` with `recipient`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
