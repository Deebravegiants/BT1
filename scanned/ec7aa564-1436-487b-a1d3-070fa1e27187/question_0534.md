# Q0534: is-healthy-with-mask via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) mint shares whose backing was never received? `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `is-healthy-with-mask` never returns a value that breaks the invariant.
