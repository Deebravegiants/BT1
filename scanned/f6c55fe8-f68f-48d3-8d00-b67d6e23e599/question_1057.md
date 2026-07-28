# Q1057: Split-account amplification via stake under many account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake()` while splitting capital across sixteen attacker EOAs splitting the same total capital into many dust positions under all attacker-visible steps happen in the same epoch before any natural reward settlement and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; sixteen attacker EOAs splitting the same total capital into many dust positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::stake()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus sixteen attacker EOAs splitting the same total capital into many dust positions using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
