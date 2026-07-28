# Q1389: Reward sniping via stake_all under victim pair unlock boundary dust threshold

## Question
Can an unprivileged attacker position around reward settlement by using `staking-pool/src/lib.rs::stake_all()` with one attacker EOA acting against a passive victim account that is already staked, the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking, and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so rewards recognized inside `internal_ping()` are attributed to the wrong share snapshot and the attacker captures value that should belong to earlier stakers?

## Target
- File/function: `staking-pool/src/lib.rs::stake_all` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping`, `last_total_balance`, `total_staked_balance`, and `total_stake_shares`
- Entrypoint: `staking-pool/src/lib.rs::stake_all()`
- Attacker controls: pre-existing unstaked balance, account splits, reward timing, and whether full-position conversion leaves dust; one attacker EOA acting against a passive victim account that is already staked; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Exploit the fact that full-position share conversion and whether it diverges from repeated partial `stake()` calls depends on when public calls trigger `internal_ping()` relative to stake ownership changes.
- Invariant to test: Rewards must accrue only to stake that was already economically at risk before the rewarded epoch; public settlement timing must not let a late entrant capture prior rewards.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Simulate a victim pre-stake, then vary whether `staking-pool/src/lib.rs::stake_all()` occurs before or after the epoch change; compare attacker reward share against the fair baseline.
