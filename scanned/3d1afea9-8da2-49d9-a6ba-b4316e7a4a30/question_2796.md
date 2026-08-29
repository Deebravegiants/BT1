# Q2796: subset via liquidate-multi: credit one side of an accounting pair without the other

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls how many entries share one price snapshot (price-feeds is passed as none) reach `subset` (mainnet/contracts/market/v0-market-vault.clar:100) in a state where it credit one side of an accounting pair without the other? Given that it tests bitmask containment, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `subset` tests bitmask containment. Reach it through `liquidate-multi` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `subset` never returns a value that breaks the invariant.
