# Q0539: calc-principal-ratio-reduction via redeem: have the same quantity scaled twice by two contracts that 

## Question
`calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) reduces scaled principal proportionally to an amount over total debt. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing the vault's available liquidity relative to the redemption, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with the vault's available liquidity relative to the redemption, and assert the attacker's net token balance change is zero or negative.
