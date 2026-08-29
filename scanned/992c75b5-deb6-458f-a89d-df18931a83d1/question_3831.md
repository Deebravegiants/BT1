# Q3831: next-liquidity-index via accrue: count one deposit as backing for two simultaneous claims

## Question
`next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing whether an earlier call in the same block already advanced last-update, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `next-liquidity-index` touches, run `accrue` with whether an earlier call in the same block already advanced last-update, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
