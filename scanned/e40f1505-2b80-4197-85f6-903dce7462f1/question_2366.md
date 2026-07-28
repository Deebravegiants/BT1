# Q2366: Split-account amplification via unstake_all under single account unlock boundary full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake_all()` while splitting capital across one attacker EOA controlling a single staking position under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; one attacker EOA controlling a single staking position; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::unstake_all()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus one attacker EOA controlling a single staking position using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
