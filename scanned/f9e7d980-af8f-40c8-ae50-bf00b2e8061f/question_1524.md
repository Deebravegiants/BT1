# Q1524: get-notional-evaluation via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) in a state where it count one deposit as backing for two simultaneous claims? Given that it folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `get-notional-evaluation` never returns a value that breaks the invariant.
