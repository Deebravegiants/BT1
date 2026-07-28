# Q2293: Attached deposit drift via unstake_all under two account unlock boundary dust threshold

## Question
Can an unprivileged attacker make `staking-pool/src/lib.rs::unstake_all()` interact with the `attached_deposit` subtraction inside `internal_ping()` under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so `last_total_balance` drifts away from the real pool backing and later public calls either mint unearned rewards or leave the accounting permanently inconsistent?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_ping`, especially `env::account_locked_balance() + env::account_balance() - env::attached_deposit()` and `last_total_balance`
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; two attacker EOAs alternating calls to compare split and merged positions; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Search for a valid public-call order where the same attached value is excluded at one step and then implicitly counted again at a later step.
- Invariant to test: `last_total_balance` must track true economic backing across deposits, withdrawals, and reward settlement; attacker-controlled attached deposits must not create phantom reward or deficit states.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Instrument `last_total_balance` before and after `staking-pool/src/lib.rs::unstake_all()` under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; compare it to actual contract balance plus locked stake and assert exact conservation.
