# Q132: Unlock-boundary bypass via deposit under two account epoch boundary full position edge

## Question
Can an unprivileged attacker route through `staking-pool/src/lib.rs::deposit()` with two attacker EOAs alternating calls to compare split and merged positions and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge so the `unstaked_available_epoch_height <= env::epoch_height()` check is satisfied one epoch too early, or so a legitimate unstaked balance becomes withdrawable only after an extra epoch, creating either early extraction or permanent user loss?

## Target
- File/function: `staking-pool/src/lib.rs::deposit` with `staking-pool/src/internal.rs::internal_deposit` and `staking-pool/src/internal.rs::internal_ping` plus `staking-pool/src/internal.rs::inner_unstake`, `unstaked_available_epoch_height`, and `staking-pool/src/internal.rs::internal_withdraw`
- Entrypoint: `staking-pool/src/lib.rs::deposit()`
- Attacker controls: attached deposit size, number of attacker accounts, follow-up call ordering, and epoch timing; two attacker EOAs alternating calls to compare split and merged positions; the attacker straddles an epoch transition where the pool has a small positive reward to settle; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Build a sequence that mixes full and partial unstakes before using `staking-pool/src/lib.rs::deposit()` near the exact unlock boundary.
- Invariant to test: Unstaked balances must become withdrawable no earlier and no later than the intended unlock epoch for the exact shares burned.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Epoch-by-epoch simulation around the fourth unlock epoch; compare partial and full unstake paths and assert that withdrawal eligibility flips exactly once at the expected boundary.
