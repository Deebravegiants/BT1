# Q0395: unpack-u16 via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) unpacks eight u16 curve fields from one packed word. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the position state the final collateral-add is validated against, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with the position state the final collateral-add is validated against, and assert the attacker's net token balance change is zero or negative.
