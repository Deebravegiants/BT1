# Q5959: accrue-user-debts via deposit: mint shares whose backing was never received

## Question
`accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) folds accrual over the position's debt list only. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing whether the vault is at a zero-supply or zero-asset edge, use that to mint shares whose backing was never received, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with whether the vault is at a zero-supply or zero-asset edge, then read `accrue-user-debts` state before and after in the same block and assert the two sides of the invariant are equal.
