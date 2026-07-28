# Q1921: Split-account amplification via unstake under single account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake()` while splitting capital across one attacker EOA controlling a single staking position under all attacker-visible steps happen in the same epoch before any natural reward settlement and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; one attacker EOA controlling a single staking position; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::unstake()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus one attacker EOA controlling a single staking position using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
