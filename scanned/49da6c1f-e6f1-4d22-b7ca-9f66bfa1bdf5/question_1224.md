# Q1224: oracle-last-update via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `oracle-last-update` never returns a value that breaks the invariant.
