# Q2240: resolve-or-create via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) in a state where it credit one side of an accounting pair without the other? Given that it allocates a user id through `increment` for whatever principal the market names, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `resolve-or-create` returns is identical in both runs; a divergence confirms the finding.
