# Q1079: Split-account amplification via stake under helper contract ping heavy dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake()` while splitting capital across an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits under a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::stake()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
