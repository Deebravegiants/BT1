# Q0126: calc-liq-factor via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `calc-liq-factor` (mainnet/contracts/market/v0-4-market.clar:703) mint shares whose backing was never received? `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:703` -> `calc-liq-factor`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `calc-liq-factor` never returns a value that breaks the invariant.
