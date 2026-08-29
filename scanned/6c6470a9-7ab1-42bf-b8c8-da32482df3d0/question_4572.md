# Q4572: is-healthy-with-mask via collateral-add: mint shares whose backing was never received

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the position's existing collateral and debt composition reach `is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) in a state where it mint shares whose backing was never received? Given that it resolves an egroup for a caller-influenced mask and applies its LTV-BORROW, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the position's existing collateral and debt composition across its boundary values through `collateral-add` in simnet and assert `is-healthy-with-mask` never returns a value that breaks the invariant.
