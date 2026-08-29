# Q3975: find via borrow: credit one side of an accounting pair without the other

## Question
`find` (mainnet/contracts/registry/v0-assets.clar:135) resolves an asset record from a principal through the `reverse` map. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `amount`, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `find` touches, run `borrow` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
