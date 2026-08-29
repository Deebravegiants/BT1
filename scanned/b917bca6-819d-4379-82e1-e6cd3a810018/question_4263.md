# Q4263: is-healthy via liquidate-multi: credit one side of an accounting pair without the other

## Question
`is-healthy` (mainnet/contracts/market/v0-4-market.clar:656) returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing which borrowers are placed early versus late in the batch, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:656` -> `is-healthy`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Reach it through `liquidate-multi` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `is-healthy` touches, run `liquidate-multi` with which borrowers are placed early versus late in the batch, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
