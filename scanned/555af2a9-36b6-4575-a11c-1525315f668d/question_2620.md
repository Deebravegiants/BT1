# Q2620: get-account-scaled-debt via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the order of accrual versus price resolution inside the let reach `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) in a state where it credit one side of an accounting pair without the other? Given that it reads one scaled debt row, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with the order of accrual versus price resolution inside the let, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
