# Q3984: refresh via collateral-remove: mint shares whose backing was never received

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls whether the position has any enabled debt row (the has-debt branch) reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it mint shares whose backing was never received? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether the position has any enabled debt row (the has-debt branch) across its boundary values through `collateral-remove` in simnet and assert `refresh` never returns a value that breaks the invariant.
