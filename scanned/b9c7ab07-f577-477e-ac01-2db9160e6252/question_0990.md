# Q990: Attached deposit drift via stake under victim pair unlock boundary full position edge

## Question
Can an unprivileged attacker make `staking-pool/src/lib.rs::stake()` interact with the `attached_deposit` subtraction inside `internal_ping()` under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so `last_total_balance` drifts away from the real pool backing and later public calls either mint unearned rewards or leave the accounting permanently inconsistent?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_ping`, especially `env::account_locked_balance() + env::account_balance() - env::attached_deposit()` and `last_total_balance`
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; one attacker EOA acting against a passive victim account that is already staked; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Search for a valid public-call order where the same attached value is excluded at one step and then implicitly counted again at a later step.
- Invariant to test: `last_total_balance` must track true economic backing across deposits, withdrawals, and reward settlement; attacker-controlled attached deposits must not create phantom reward or deficit states.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Instrument `last_total_balance` before and after `staking-pool/src/lib.rs::stake()` under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; compare it to actual contract balance plus locked stake and assert exact conservation.
