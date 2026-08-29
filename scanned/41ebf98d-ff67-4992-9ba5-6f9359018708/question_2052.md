# Q2052: calc-treasury-lp-preview via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the vault's available liquidity relative to the redemption reach `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) in a state where it credit one side of an accounting pair without the other? Given that it divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault's available liquidity relative to the redemption across its boundary values through `redeem` in simnet and assert `calc-treasury-lp-preview` never returns a value that breaks the invariant.
