# Q1903: Unlock-boundary bypass via unstake under many account ping heavy dust threshold

## Question
Can an unprivileged attacker route through `staking-pool/src/lib.rs::unstake()` with sixteen attacker EOAs splitting the same total capital into many dust positions and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding so the `unstaked_available_epoch_height <= env::epoch_height()` check is satisfied one epoch too early, or so a legitimate unstaked balance becomes withdrawable only after an extra epoch, creating either early extraction or permanent user loss?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::inner_unstake`, `unstaked_available_epoch_height`, and `staking-pool/src/internal.rs::internal_withdraw`
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; sixteen attacker EOAs splitting the same total capital into many dust positions; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Build a sequence that mixes full and partial unstakes before using `staking-pool/src/lib.rs::unstake()` near the exact unlock boundary.
- Invariant to test: Unstaked balances must become withdrawable no earlier and no later than the intended unlock epoch for the exact shares burned.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Epoch-by-epoch simulation around the fourth unlock epoch; compare partial and full unstake paths and assert that withdrawal eligibility flips exactly once at the expected boundary.
