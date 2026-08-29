# Q2648: principal-ratio-reduction via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) in a state where it credit one side of an accounting pair without the other? Given that it derives a principal reduction from an amount, the scaled principal and the previewed debt, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `principal-ratio-reduction` returns is identical in both runs; a divergence confirms the finding.
