# Q5936: insert via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `insert` (mainnet/contracts/market/v0-market-vault.clar:159) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it rewrites the whole registry entry for a user id, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `insert` returns is identical in both runs; a divergence confirms the finding.
