# Q3064: Cross-user order dependence via withdraw under many account ping heavy full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::withdraw()` while a victim position is already live, and by choosing the exact public-call order under a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, make the victim and attacker end with different total claimable value than they would under the economically equivalent fair ordering?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `internal_stake`, `inner_unstake`, and per-account share accounting
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; sixteen attacker EOAs splitting the same total capital into many dust positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Treat public call ordering itself as the attack surface: attacker and victim both use valid public functions, but the attacker chooses when `staking-pool/src/lib.rs::withdraw()` triggers accounting transitions.
- Invariant to test: When total stake, rewards, and withdrawals are economically equivalent, user value split should not depend on attacker-chosen ordering beyond legitimate time-at-risk differences.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Differential test two traces with identical actors and balances but swapped attacker/victim ordering around `staking-pool/src/lib.rs::withdraw()`; assert equivalent final economics unless time-at-risk legitimately differs.
