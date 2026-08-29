# Q5318: resolve-or-create via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the `ft` trait principal deciding which vault is routed to, can an unprivileged attacker make `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) count one deposit as backing for two simultaneous claims? `resolve-or-create` allocates a user id through `increment` for whatever principal the market names, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the `ft` trait principal deciding which vault is routed to varied, and assert that the value `resolve-or-create` returns is identical in both runs; a divergence confirms the finding.
