# Q5427: next-index via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
`next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `next-index` touches, run `borrow` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
