# Q1948: system-borrow via liquidate: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `system-borrow` (mainnet/contracts/vault/v0-vault-stx.clar:865) in a state where it count one deposit as backing for two simultaneous claims? Given that it independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:865` -> `system-borrow`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `system-borrow` independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with which collateral and debt asset pair is targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
