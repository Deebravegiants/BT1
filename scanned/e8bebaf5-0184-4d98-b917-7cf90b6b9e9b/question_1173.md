# Q1173: unpack-u16 via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the block time at which accrual is first triggered in a block, drive `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) — which unpacks eight u16 curve fields from one packed word — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `unpack-u16` touches, run `accrue` with the block time at which accrual is first triggered in a block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
