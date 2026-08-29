# Q4599: get-account-scaled-debt via repay: credit one side of an accounting pair without the other

## Question
`get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) reads one scaled debt row. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `get-account-scaled-debt` touches, run `repay` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
