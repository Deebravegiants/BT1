# Q5398: resolve-ststx via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `receiver` for the underlying leg, can an unprivileged attacker make `resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) count one deposit as backing for two simultaneous claims? `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `receiver` for the underlying leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
