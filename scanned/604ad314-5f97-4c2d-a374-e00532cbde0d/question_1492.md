# Q1492: send-tokens via liquidate: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) in a state where it count one deposit as backing for two simultaneous claims? Given that it pushes an asset to a caller-chosen recipient principal, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with which collateral and debt asset pair is targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
