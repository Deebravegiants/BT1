# Q0555: zip via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
`zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) pairs the utilization and rate point lists element by element. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing the block and transaction position at which the external ratio is fetched, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `zip` touches, run `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
