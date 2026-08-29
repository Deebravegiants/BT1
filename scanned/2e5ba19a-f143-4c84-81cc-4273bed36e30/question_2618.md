# Q2618: add-user-collateral via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling whether the position has any enabled debt row (the has-debt branch), can an unprivileged attacker make `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) have the same quantity scaled twice by two contracts that round differently? `add-user-collateral` adds to the collateral row with a graceful u0 default, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with whether the position has any enabled debt row (the has-debt branch) varied, and assert that the value `add-user-collateral` returns is identical in both runs; a divergence confirms the finding.
