# Q0085: accrue-user-debts via deposit: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling whether the vault is at a zero-supply or zero-asset edge, drive `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) — which folds accrual over the position's debt list only — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with whether the vault is at a zero-supply or zero-asset edge, then read `accrue-user-debts` state before and after in the same block and assert the two sides of the invariant are equal.
