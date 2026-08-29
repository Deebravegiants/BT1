# Q1572: iter-price-multi via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `iter-price-multi` (mainnet/contracts/market/v0-4-market.clar:405) in a state where it count one deposit as backing for two simultaneous claims? Given that it carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:405` -> `iter-price-multi`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `iter-price-multi` never returns a value that breaks the invariant.
