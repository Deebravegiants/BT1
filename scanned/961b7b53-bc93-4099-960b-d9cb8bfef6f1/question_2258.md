# Q2258: Reward sniping via unstake_all under many account same epoch full position edge

## Question
Can an unprivileged attacker position around reward settlement by using `staking-pool/src/lib.rs::unstake_all()` with sixteen attacker EOAs splitting the same total capital into many dust positions, all attacker-visible steps happen in the same epoch before any natural reward settlement, and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so rewards recognized inside `internal_ping()` are attributed to the wrong share snapshot and the attacker captures value that should belong to earlier stakers?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and `total_stake_shares`
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; sixteen attacker EOAs splitting the same total capital into many dust positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Exploit the fact that full-position unstake semantics and whether they diverge from repeated partial `unstake()` calls depends on when public calls trigger `internal_ping()` relative to stake ownership changes.
- Invariant to test: Rewards must accrue only to stake that was already economically at risk before the rewarded epoch; public settlement timing must not let a late entrant capture prior rewards.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Simulate a victim pre-stake, then vary whether `staking-pool/src/lib.rs::unstake_all()` occurs before or after the epoch change; compare attacker reward share against the fair baseline.
