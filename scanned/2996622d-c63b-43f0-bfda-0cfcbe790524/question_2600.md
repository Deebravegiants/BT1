# Q2600: send-underlying via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it credit one side of an accounting pair without the other? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `min-underlying` varied, and assert that the value `send-underlying` returns is identical in both runs; a divergence confirms the finding.
