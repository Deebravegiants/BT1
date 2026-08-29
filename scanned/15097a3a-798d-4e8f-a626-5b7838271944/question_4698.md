# Q4698: check-confidence via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) destroy value through a truncation the opposite operation does not restore? `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `borrow` in simnet and assert `check-confidence` never returns a value that breaks the invariant.
