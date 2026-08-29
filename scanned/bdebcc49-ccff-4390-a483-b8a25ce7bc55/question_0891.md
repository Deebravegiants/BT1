# Q0891: total-supply-preview via transfer: have the same quantity scaled twice by two contracts that 

## Question
`total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing the timing relative to a pledge or a liquidation, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `total-supply-preview` touches, run `transfer` with the timing relative to a pledge or a liquidation, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
