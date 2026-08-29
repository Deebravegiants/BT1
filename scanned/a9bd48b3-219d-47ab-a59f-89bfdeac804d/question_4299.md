# Q4299: calc-multiplier-delta via deposit: credit one side of an accounting pair without the other

## Question
`calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) compounds a rate over `time-delta` with a caller-independent rounding flag. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `recipient`, including a contract principal, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `calc-multiplier-delta` touches, run `deposit` with `recipient`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
