# Q1498: Split-account amplification via stake_all under many account same epoch full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake_all()` while splitting capital across sixteen attacker EOAs splitting the same total capital into many dust positions under all attacker-visible steps happen in the same epoch before any natural reward settlement and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::stake_all` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::stake_all()`
- Attacker controls: pre-existing unstaked balance, account splits, reward timing, and whether full-position conversion leaves dust; sixteen attacker EOAs splitting the same total capital into many dust positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::stake_all()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus sixteen attacker EOAs splitting the same total capital into many dust positions using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
