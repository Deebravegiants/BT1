# Q1884: find-collateral-amount via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns u0 for an absent asset, making a missing row indistinguishable from a zero holding, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `find-collateral-amount` never returns a value that breaks the invariant.
