# Q2076: collateral-add via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) in a state where it credit one side of an accounting pair without the other? Given that it evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `collateral-add` never returns a value that breaks the invariant.
