# Q1392: remove-user-scaled-debt via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `remove-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:244) in a state where it count one deposit as backing for two simultaneous claims? Given that it deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:244` -> `remove-user-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `remove-user-scaled-debt` never returns a value that breaks the invariant.
