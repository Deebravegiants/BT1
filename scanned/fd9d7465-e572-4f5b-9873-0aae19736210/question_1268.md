# Q1268: interpolate-rate via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) in a state where it count one deposit as backing for two simultaneous claims? Given that it interpolates between packed u16 curve points, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with vault share price at the moment of the deposit leg varied, and assert that the value `interpolate-rate` returns is identical in both runs; a divergence confirms the finding.
