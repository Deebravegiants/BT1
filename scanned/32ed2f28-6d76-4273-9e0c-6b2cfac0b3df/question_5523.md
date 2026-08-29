# Q5523: next-liquidity-index via deposit: make the per-user ledger and the vault aggregate disagree 

## Question
`next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `recipient`, including a contract principal, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `deposit` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `next-liquidity-index` touches, run `deposit` with `recipient`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
