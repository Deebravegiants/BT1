# Q2352: oracle-timestamp-fresh via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `oracle-timestamp-fresh` (mainnet/contracts/market/v0-4-market.clar:365) in a state where it credit one side of an accounting pair without the other? Given that it sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:365` -> `oracle-timestamp-fresh`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `oracle-timestamp-fresh` sets `delta` to u0 whenever `ts` exceeds `stacks-block-time`, so a future timestamp is maximally fresh, then requires `(>= ts prev)`. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `oracle-timestamp-fresh` never returns a value that breaks the invariant.
