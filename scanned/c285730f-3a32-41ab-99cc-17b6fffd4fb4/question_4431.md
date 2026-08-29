# Q4431: calc-index-next via collateral-add: credit one side of an accounting pair without the other

## Question
`calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) applies a multiplier to the current index. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the `ft` trait principal, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-index-next` touches, run `collateral-add` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
