# Q1959: total-debt via redeem: destroy value through a truncation the opposite operation 

## Question
`total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) computes cumulative debt from `principal-scaled` and `index`. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing `amount` of shares burned, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `total-debt` touches, run `redeem` with `amount` of shares burned, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
