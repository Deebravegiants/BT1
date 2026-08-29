# Q1270: get-position via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) record a repayment larger than the value actually delivered? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the vault whose share price the redemption moves, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
