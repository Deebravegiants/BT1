# Q2316: get-cached-indexes via liquidate-redeem: credit one side of an accounting pair without the other

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the redemption receiver reach `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) in a state where it credit one side of an accounting pair without the other? Given that it reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `get-cached-indexes` never returns a value that breaks the invariant.
