# Q2391: Split-account amplification via unstake_all under victim pair ping heavy dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake_all()` while splitting capital across one attacker EOA acting against a passive victim account that is already staked under a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; one attacker EOA acting against a passive victim account that is already staked; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::unstake_all()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus one attacker EOA acting against a passive victim account that is already staked using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
