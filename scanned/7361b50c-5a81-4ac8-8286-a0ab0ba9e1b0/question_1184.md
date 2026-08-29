# Q1184: ubalance via redeem: count one deposit as backing for two simultaneous claims

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) in a state where it count one deposit as backing for two simultaneous claims? Given that it reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `ubalance` returns is identical in both runs; a divergence confirms the finding.
