# Q0538: debt-preview via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `recipient`, including a contract principal, can an unprivileged attacker make `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) mint shares whose backing was never received? `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `deposit` with `recipient`, including a contract principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
