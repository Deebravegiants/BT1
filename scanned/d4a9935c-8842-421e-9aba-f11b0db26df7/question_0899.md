# Q0899: zip via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
`zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) pairs the utilization and rate point lists element by element. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing which borrowers are placed early versus late in the batch, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with which borrowers are placed early versus late in the batch, and assert the attacker's net token balance change is zero or negative.
