# Q0699: linear-interpolate via redeem: have the same quantity scaled twice by two contracts that 

## Question
`linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) interpolates between two points, dividing by `(- x2 x1)`. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing the vault's available liquidity relative to the redemption, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `linear-interpolate` touches, run `redeem` with the vault's available liquidity relative to the redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
