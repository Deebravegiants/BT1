# Q4044: lookup via collateral-remove: mint shares whose backing was never received

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls whether the position has any enabled debt row (the has-debt branch) reach `lookup` (mainnet/contracts/registry/v0-assets.clar:139) in a state where it mint shares whose backing was never received? Given that it returns the registry record, including the `decimals` captured once at registration, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the position has any enabled debt row (the has-debt branch) across its boundary values through `collateral-remove` in simnet and assert `lookup` never returns a value that breaks the invariant.
