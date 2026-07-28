# Q3935: Cross-user order dependence via ping under two account ping heavy dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::ping()` while a victim position is already live, and by choosing the exact public-call order under a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, make the victim and attacker end with different total claimable value than they would under the economically equivalent fair ordering?

## Target
- File/function: `staking-pool/src/lib.rs::ping` with `staking-pool/src/internal.rs::internal_ping` and reward distribution into `total_staked_balance` / `total_stake_shares` plus `staking-pool/src/internal.rs::internal_ping`, `internal_stake`, `inner_unstake`, and per-account share accounting
- Entrypoint: `staking-pool/src/lib.rs::ping()`
- Attacker controls: when `ping()` is triggered, how often it is repeated, what attacker position exists before it, and whether a victim position is already live; two attacker EOAs alternating calls to compare split and merged positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Treat public call ordering itself as the attack surface: attacker and victim both use valid public functions, but the attacker chooses when `staking-pool/src/lib.rs::ping()` triggers accounting transitions.
- Invariant to test: When total stake, rewards, and withdrawals are economically equivalent, user value split should not depend on attacker-chosen ordering beyond legitimate time-at-risk differences.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Differential test two traces with identical actors and balances but swapped attacker/victim ordering around `staking-pool/src/lib.rs::ping()`; assert equivalent final economics unless time-at-risk legitimately differs.
