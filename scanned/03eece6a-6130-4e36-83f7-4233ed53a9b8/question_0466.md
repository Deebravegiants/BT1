# Q0466: calc-utilization via borrow: mint shares whose backing was never received

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) mint shares whose backing was never received? `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
