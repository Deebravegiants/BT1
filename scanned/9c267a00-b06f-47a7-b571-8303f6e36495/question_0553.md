# Q0553: accrue via deposit: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `recipient`, including a contract principal, drive `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) — which advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:835` -> `accrue`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with `recipient`, including a contract principal, then read `accrue` state before and after in the same block and assert the two sides of the invariant are equal.
