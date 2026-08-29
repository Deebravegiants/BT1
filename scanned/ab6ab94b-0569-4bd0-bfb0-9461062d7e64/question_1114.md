# Q1114: is-liquidation-paused via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `is-liquidation-paused` (mainnet/contracts/market/v0-4-market.clar:691) record a repayment larger than the value actually delivered? `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:691` -> `is-liquidation-paused`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the vault whose share price the redemption moves, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
