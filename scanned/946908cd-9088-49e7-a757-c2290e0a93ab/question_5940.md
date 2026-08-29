# Q5940: get-account-scaled-debt via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls how many entries share one price snapshot (price-feeds is passed as none) reach `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it reads one scaled debt row, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `get-account-scaled-debt` never returns a value that breaks the invariant.
