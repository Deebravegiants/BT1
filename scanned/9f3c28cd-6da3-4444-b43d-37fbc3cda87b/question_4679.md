# Q4679: resolve-interpolation-points via redeem: credit one side of an accounting pair without the other

## Question
`resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) selects the bracketing curve points for a utilization. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `recipient`, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with `recipient`, and assert the attacker's net token balance change is zero or negative.
