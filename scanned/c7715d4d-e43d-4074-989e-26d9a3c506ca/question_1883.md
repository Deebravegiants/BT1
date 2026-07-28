# Q1883: Unlock-boundary bypass via unstake under single account epoch boundary dust threshold

## Question
Can an unprivileged attacker route through `staking-pool/src/lib.rs::unstake()` with one attacker EOA controlling a single staking position and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding so the `unstaked_available_epoch_height <= env::epoch_height()` check is satisfied one epoch too early, or so a legitimate unstaked balance becomes withdrawable only after an extra epoch, creating either early extraction or permanent user loss?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::inner_unstake`, `unstaked_available_epoch_height`, and `staking-pool/src/internal.rs::internal_withdraw`
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; one attacker EOA controlling a single staking position; the attacker straddles an epoch transition where the pool has a small positive reward to settle; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Build a sequence that mixes full and partial unstakes before using `staking-pool/src/lib.rs::unstake()` near the exact unlock boundary.
- Invariant to test: Unstaked balances must become withdrawable no earlier and no later than the intended unlock epoch for the exact shares burned.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Epoch-by-epoch simulation around the fourth unlock epoch; compare partial and full unstake paths and assert that withdrawal eligibility flips exactly once at the expected boundary.
