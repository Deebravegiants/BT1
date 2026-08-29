# Q3615: unpack-u16 via redeem: count one deposit as backing for two simultaneous claims

## Question
`unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) unpacks eight u16 curve fields from one packed word. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `recipient`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `unpack-u16` touches, run `redeem` with `recipient`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
