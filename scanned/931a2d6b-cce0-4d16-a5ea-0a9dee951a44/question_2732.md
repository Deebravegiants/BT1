# Q2732: Attached deposit drift via withdraw under two account epoch boundary full position edge

## Question
Can an unprivileged attacker make `staking-pool/src/lib.rs::withdraw()` interact with the `attached_deposit` subtraction inside `internal_ping()` under the attacker straddles an epoch transition where the pool has a small positive reward to settle and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so `last_total_balance` drifts away from the real pool backing and later public calls either mint unearned rewards or leave the accounting permanently inconsistent?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, especially `env::account_locked_balance() + env::account_balance() - env::attached_deposit()` and `last_total_balance`
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; two attacker EOAs alternating calls to compare split and merged positions; the attacker straddles an epoch transition where the pool has a small positive reward to settle; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Search for a valid public-call order where the same attached value is excluded at one step and then implicitly counted again at a later step.
- Invariant to test: `last_total_balance` must track true economic backing across deposits, withdrawals, and reward settlement; attacker-controlled attached deposits must not create phantom reward or deficit states.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Instrument `last_total_balance` before and after `staking-pool/src/lib.rs::withdraw()` under the attacker straddles an epoch transition where the pool has a small positive reward to settle; compare it to actual contract balance plus locked stake and assert exact conservation.
