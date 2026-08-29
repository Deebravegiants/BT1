# Q2410: total-assets via deposit: have the same quantity scaled twice by two contracts that 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `min-out`, can an unprivileged attacker make `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) have the same quantity scaled twice by two contracts that round differently? `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `deposit` with `min-out`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
