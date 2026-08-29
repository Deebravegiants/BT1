# Q4692: uint-to-list-u64 via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) in a state where it mint shares whose backing was never received? Given that it expands a bitmap into a 64-element list, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `uint-to-list-u64` never returns a value that breaks the invariant.
