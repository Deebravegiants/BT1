# Q2192: increment via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `increment` (mainnet/contracts/market/v0-market-vault.clar:137) in a state where it credit one side of an accounting pair without the other? Given that it advances the user-id nonce, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `increment` advances the user-id nonce. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `increment` returns is identical in both runs; a divergence confirms the finding.
