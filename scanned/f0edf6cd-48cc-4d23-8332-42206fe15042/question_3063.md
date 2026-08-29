# Q3063: calc-liq-factor via liquidate: count one deposit as backing for two simultaneous claims

## Question
`calc-liq-factor` (mainnet/contracts/market/v0-4-market.clar:703) computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing the `price-feeds` buffers and their ordering, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:703` -> `calc-liq-factor`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-liq-factor` touches, run `liquidate` with the `price-feeds` buffers and their ordering, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
