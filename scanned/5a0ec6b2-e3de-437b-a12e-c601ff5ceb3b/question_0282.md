# Q0282: resolve-or-create via borrow: mint shares whose backing was never received

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the order of accrual versus price resolution inside the let, can an unprivileged attacker make `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) mint shares whose backing was never received? `resolve-or-create` allocates a user id through `increment` for whatever principal the market names, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the order of accrual versus price resolution inside the let across its boundary values through `borrow` in simnet and assert `resolve-or-create` never returns a value that breaks the invariant.
