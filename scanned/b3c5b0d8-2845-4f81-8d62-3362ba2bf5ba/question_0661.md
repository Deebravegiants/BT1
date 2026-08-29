# Q0661: check-confidence via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `amount` used for BOTH the collateral removal and the share redemption, drive `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) — which compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, then read `check-confidence` state before and after in the same block and assert the two sides of the invariant are equal.
