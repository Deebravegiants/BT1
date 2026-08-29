# Q3855: zip via accrue: count one deposit as backing for two simultaneous claims

## Question
`zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) pairs the utilization and rate point lists element by element. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing whether an earlier call in the same block already advanced last-update, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `zip` touches, run `accrue` with whether an earlier call in the same block already advanced last-update, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
