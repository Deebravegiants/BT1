# Q1315: Cross-user order dependence via stake under helper contract epoch boundary dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake()` while a victim position is already live, and by choosing the exact public-call order under the attacker straddles an epoch transition where the pool has a small positive reward to settle and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, make the victim and attacker end with different total claimable value than they would under the economically equivalent fair ordering?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping`, `internal_stake`, `inner_unstake`, and per-account share accounting
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; the attacker straddles an epoch transition where the pool has a small positive reward to settle; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Treat public call ordering itself as the attack surface: attacker and victim both use valid public functions, but the attacker chooses when `staking-pool/src/lib.rs::stake()` triggers accounting transitions.
- Invariant to test: When total stake, rewards, and withdrawals are economically equivalent, user value split should not depend on attacker-chosen ordering beyond legitimate time-at-risk differences.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Differential test two traces with identical actors and balances but swapped attacker/victim ordering around `staking-pool/src/lib.rs::stake()`; assert equivalent final economics unless time-at-risk legitimately differs.
