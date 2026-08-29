# Q1512: find-and-resolve-asset-value via liquidate: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `borrower`, any third-party principal reach `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) in a state where it count one deposit as backing for two simultaneous claims? Given that it reuses an already-resolved price from the asset list and returns u0 when the asset is not found, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `borrower`, any third-party principal across its boundary values through `liquidate` in simnet and assert `find-and-resolve-asset-value` never returns a value that breaks the invariant.
