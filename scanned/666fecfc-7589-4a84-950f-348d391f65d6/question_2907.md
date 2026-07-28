# Q2907: Full-vs-partial divergence via withdraw under victim pair epoch boundary dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::withdraw()` under the attacker straddles an epoch transition where the pool has a small positive reward to settle and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to reach a different economic state than the logically equivalent sequence of partial calls, such that `stake_all`/`unstake_all`/`withdraw_all` semantics diverge from repeated `stake`/`unstake`/`withdraw` and leak value or trap dust?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/lib.rs` full-position methods versus partial-position methods and their shared internals
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; one attacker EOA acting against a passive victim account that is already staked; the attacker straddles an epoch transition where the pool has a small positive reward to settle; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare a one-shot full-position transition against the equivalent set of partial transitions while holding total capital and epoch timing constant.
- Invariant to test: Economically equivalent full and partial public paths must lead to the same total claimable value, unlock timing, and pool accounting state.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Build paired simulations that differ only by using `staking-pool/src/lib.rs::withdraw()` versus the equivalent partial sequence; assert identical balances, share totals, and unlock epochs.
