# Q2679: calc-liq-factor via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
`calc-liq-factor` (mainnet/contracts/market/v0-4-market.clar:703) computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the full batch list and its ordering, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:703` -> `calc-liq-factor`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `calc-liq-factor` touches, run `liquidate-multi` with the full batch list and its ordering, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
