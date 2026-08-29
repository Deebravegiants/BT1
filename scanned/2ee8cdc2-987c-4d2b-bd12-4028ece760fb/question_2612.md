# Q2612: collateral-remove via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) in a state where it credit one side of an accounting pair without the other? Given that it decrements the map and writes the entry before `send-tokens` executes, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `collateral-remove` returns is identical in both runs; a divergence confirms the finding.
