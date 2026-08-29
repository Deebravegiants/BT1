# Q0490: calc-cumulative-debt via liquidate-redeem: mint shares whose backing was never received

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) mint shares whose backing was never received? `calc-cumulative-debt` multiplies scaled principal by an index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the redemption receiver, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
