# Q2511: accrue via deposit: destroy value through a truncation the opposite operation 

## Question
`accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `recipient`, including a contract principal, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:835` -> `accrue`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `accrue` touches, run `deposit` with `recipient`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
