# Q0802: calc-multiplier-delta via liquidate-multi: mint shares whose backing was never received

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) mint shares whose backing was never received? `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
