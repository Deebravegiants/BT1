# Q2234: get-position via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) have the same quantity scaled twice by two contracts that round differently? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with whether the position has any enabled debt row (the has-debt branch) varied, and assert that the value `get-position` returns is identical in both runs; a divergence confirms the finding.
