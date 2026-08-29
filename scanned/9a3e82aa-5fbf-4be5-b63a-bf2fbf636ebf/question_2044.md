# Q2044: refresh via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it credit one side of an accounting pair without the other? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with call ordering within the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
