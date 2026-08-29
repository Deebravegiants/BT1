# Q5222: interest-rate via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) count one deposit as backing for two simultaneous claims? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `interest-rate` returns is identical in both runs; a divergence confirms the finding.
