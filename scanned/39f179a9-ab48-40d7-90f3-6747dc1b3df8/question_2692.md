# Q2692: Reward sniping via withdraw under two account epoch boundary full position edge

## Question
Can an unprivileged attacker position around reward settlement by using `staking-pool/src/lib.rs::withdraw()` with two attacker EOAs alternating calls to compare split and merged positions, the attacker straddles an epoch transition where the pool has a small positive reward to settle, and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so rewards recognized inside `internal_ping()` are attributed to the wrong share snapshot and the attacker captures value that should belong to earlier stakers?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and `total_stake_shares`
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; two attacker EOAs alternating calls to compare split and merged positions; the attacker straddles an epoch transition where the pool has a small positive reward to settle; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Exploit the fact that unlock enforcement, `last_total_balance` updates, and whether liquid withdrawals can exceed fair entitlement depends on when public calls trigger `internal_ping()` relative to stake ownership changes.
- Invariant to test: Rewards must accrue only to stake that was already economically at risk before the rewarded epoch; public settlement timing must not let a late entrant capture prior rewards.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Simulate a victim pre-stake, then vary whether `staking-pool/src/lib.rs::withdraw()` occurs before or after the epoch change; compare attacker reward share against the fair baseline.
