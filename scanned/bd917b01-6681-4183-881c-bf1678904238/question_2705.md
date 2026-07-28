# Q2705: Reward sniping via withdraw under victim pair same epoch dust threshold

## Question
Can an unprivileged attacker position around reward settlement by using `staking-pool/src/lib.rs::withdraw()` with one attacker EOA acting against a passive victim account that is already staked, all attacker-visible steps happen in the same epoch before any natural reward settlement, and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so rewards recognized inside `internal_ping()` are attributed to the wrong share snapshot and the attacker captures value that should belong to earlier stakers?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and `total_stake_shares`
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; one attacker EOA acting against a passive victim account that is already staked; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Exploit the fact that unlock enforcement, `last_total_balance` updates, and whether liquid withdrawals can exceed fair entitlement depends on when public calls trigger `internal_ping()` relative to stake ownership changes.
- Invariant to test: Rewards must accrue only to stake that was already economically at risk before the rewarded epoch; public settlement timing must not let a late entrant capture prior rewards.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Simulate a victim pre-stake, then vary whether `staking-pool/src/lib.rs::withdraw()` occurs before or after the epoch change; compare attacker reward share against the fair baseline.
