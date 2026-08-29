# Q2328: calc-treasury-lp-preview via transfer: credit one side of an accounting pair without the other

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls `amount` reach `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) in a state where it credit one side of an accounting pair without the other? Given that it divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `calc-treasury-lp-preview` never returns a value that breaks the invariant.
