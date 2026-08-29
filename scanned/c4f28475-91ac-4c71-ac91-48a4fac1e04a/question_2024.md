# Q2024: get-account-scaled-debt via liquidate-multi: credit one side of an accounting pair without the other

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls how many entries share one price snapshot (price-feeds is passed as none) reach `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) in a state where it credit one side of an accounting pair without the other? Given that it reads one scaled debt row, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `liquidate-multi` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with how many entries share one price snapshot (price-feeds is passed as none) varied, and assert that the value `get-account-scaled-debt` returns is identical in both runs; a divergence confirms the finding.
