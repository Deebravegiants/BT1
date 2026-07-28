# Q2021: Full-vs-partial divergence via unstake under many account unlock boundary dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake()` under the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to reach a different economic state than the logically equivalent sequence of partial calls, such that `stake_all`/`unstake_all`/`withdraw_all` semantics diverge from repeated `stake`/`unstake`/`withdraw` and leak value or trap dust?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/lib.rs` full-position methods versus partial-position methods and their shared internals
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; sixteen attacker EOAs splitting the same total capital into many dust positions; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Compare a one-shot full-position transition against the equivalent set of partial transitions while holding total capital and epoch timing constant.
- Invariant to test: Economically equivalent full and partial public paths must lead to the same total claimable value, unlock timing, and pool accounting state.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Build paired simulations that differ only by using `staking-pool/src/lib.rs::unstake()` versus the equivalent partial sequence; assert identical balances, share totals, and unlock epochs.
