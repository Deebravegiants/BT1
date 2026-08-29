# Q1544: socialize-debt via liquidate: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `socialize-debt` (mainnet/contracts/vault/v0-vault-stx.clar:944) in a state where it count one deposit as backing for two simultaneous claims? Given that it writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:944` -> `socialize-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `min-collateral-expected` varied, and assert that the value `socialize-debt` returns is identical in both runs; a divergence confirms the finding.
