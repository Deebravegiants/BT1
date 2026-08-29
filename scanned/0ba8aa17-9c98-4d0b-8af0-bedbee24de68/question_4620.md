# Q4620: refresh via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it mint shares whose backing was never received? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `refresh` never returns a value that breaks the invariant.
