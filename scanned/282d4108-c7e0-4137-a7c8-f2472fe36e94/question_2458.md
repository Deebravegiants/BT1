# Q2458: Full-vs-partial divergence via unstake_all under many account same epoch full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake_all()` under all attacker-visible steps happen in the same epoch before any natural reward settlement and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to reach a different economic state than the logically equivalent sequence of partial calls, such that `stake_all`/`unstake_all`/`withdraw_all` semantics diverge from repeated `stake`/`unstake`/`withdraw` and leak value or trap dust?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/lib.rs` full-position methods versus partial-position methods and their shared internals
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; sixteen attacker EOAs splitting the same total capital into many dust positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Compare a one-shot full-position transition against the equivalent set of partial transitions while holding total capital and epoch timing constant.
- Invariant to test: Economically equivalent full and partial public paths must lead to the same total claimable value, unlock timing, and pool accounting state.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Build paired simulations that differ only by using `staking-pool/src/lib.rs::unstake_all()` versus the equivalent partial sequence; assert identical balances, share totals, and unlock epochs.
