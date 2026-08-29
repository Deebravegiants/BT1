# Q2340: next-index via accrue: credit one side of an accounting pair without the other

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it credit one side of an accounting pair without the other? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `accrue` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `next-index` never returns a value that breaks the invariant.
