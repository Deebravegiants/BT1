# Q1400: Reward sniping via stake_all under helper contract ping heavy full position edge

## Question
Can an unprivileged attacker position around reward settlement by using `staking-pool/src/lib.rs::stake_all()` with an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits, a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step, and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so rewards recognized inside `internal_ping()` are attributed to the wrong share snapshot and the attacker captures value that should belong to earlier stakers?

## Target
- File/function: `staking-pool/src/lib.rs::stake_all` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and `total_stake_shares`
- Entrypoint: `staking-pool/src/lib.rs::stake_all()`
- Attacker controls: pre-existing unstaked balance, account splits, reward timing, and whether full-position conversion leaves dust; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Exploit the fact that full-position share conversion and whether it diverges from repeated partial `stake()` calls depends on when public calls trigger `internal_ping()` relative to stake ownership changes.
- Invariant to test: Rewards must accrue only to stake that was already economically at risk before the rewarded epoch; public settlement timing must not let a late entrant capture prior rewards.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Simulate a victim pre-stake, then vary whether `staking-pool/src/lib.rs::stake_all()` occurs before or after the epoch change; compare attacker reward share against the fair baseline.
