# Q4671: subset via borrow: credit one side of an accounting pair without the other

## Question
`subset` (mainnet/contracts/market/v0-market-vault.clar:100) tests bitmask containment. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `amount`, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `subset` tests bitmask containment. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `subset` touches, run `borrow` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
