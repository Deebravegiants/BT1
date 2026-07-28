# Q3958: Cross-user order dependence via ping under helper contract unlock boundary full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::ping()` while a victim position is already live, and by choosing the exact public-call order under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, make the victim and attacker end with different total claimable value than they would under the economically equivalent fair ordering?

## Target
- File/function: `staking-pool/src/lib.rs::ping` with `staking-pool/src/internal.rs::internal_ping` and reward distribution into `total_staked_balance` / `total_stake_shares` plus `staking-pool/src/internal.rs::internal_ping`, `internal_stake`, `inner_unstake`, and per-account share accounting
- Entrypoint: `staking-pool/src/lib.rs::ping()`
- Attacker controls: when `ping()` is triggered, how often it is repeated, what attacker position exists before it, and whether a victim position is already live; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Treat public call ordering itself as the attack surface: attacker and victim both use valid public functions, but the attacker chooses when `staking-pool/src/lib.rs::ping()` triggers accounting transitions.
- Invariant to test: When total stake, rewards, and withdrawals are economically equivalent, user value split should not depend on attacker-chosen ordering beyond legitimate time-at-risk differences.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Differential test two traces with identical actors and balances but swapped attacker/victim ordering around `staking-pool/src/lib.rs::ping()`; assert equivalent final economics unless time-at-risk legitimately differs.
