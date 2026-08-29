# Q0912: total-debt via accrue: destroy value through a truncation the opposite operation 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `total-debt` never returns a value that breaks the invariant.
