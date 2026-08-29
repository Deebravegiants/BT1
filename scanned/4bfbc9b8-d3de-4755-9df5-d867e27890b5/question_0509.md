# Q0509: accrue-user-debts via redeem: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling the vault's available liquidity relative to the redemption, drive `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) — which folds accrual over the position's debt list only — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `redeem` call, then the attacker-shaped one with the vault's available liquidity relative to the redemption, and assert the attacker's net token balance change is zero or negative.
