# Q2420: total-assets via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the block time at which accrual is first triggered in a block reach `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) in a state where it credit one side of an accounting pair without the other? Given that it adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the block time at which accrual is first triggered in a block varied, and assert that the value `total-assets` returns is identical in both runs; a divergence confirms the finding.
