# Q3278: Split-account amplification via withdraw_all under helper contract unlock boundary full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::withdraw_all()` while splitting capital across an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge, so per-account rounding accumulates more favorable share or withdrawal outcomes than the same capital would receive in one account and the difference comes from other stakers?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw_all` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_stake`, `inner_unstake`, and per-account share state in `accounts`
- Entrypoint: `staking-pool/src/lib.rs::withdraw_all()`
- Attacker controls: full unstaked balance, epoch height, intervening `ping()` calls, and whether dust or extra liquid value remains after full withdrawal; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Compare one large position against the same capital fragmented across many attacker-controlled positions, with `staking-pool/src/lib.rs::withdraw_all()` as the key transition.
- Invariant to test: Capital fragmentation alone must not increase aggregate claimable value relative to the same total principal in one account.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Run differential tests: one consolidated attacker account versus an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits using identical total principal and call sequence; assert equal or lower aggregate attacker value in the split case.
