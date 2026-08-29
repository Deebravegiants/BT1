# Q0288: is-healthy via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls the `price-feeds` buffers and their ordering reach `is-healthy` (mainnet/contracts/market/v0-4-market.clar:656) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:656` -> `is-healthy`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `is-healthy` never returns a value that breaks the invariant.
