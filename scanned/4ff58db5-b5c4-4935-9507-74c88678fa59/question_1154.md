# Q1154: Full-vs-partial divergence via stake under helper contract same epoch full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake()` under all attacker-visible steps happen in the same epoch before any natural reward settlement and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to reach a different economic state than the logically equivalent sequence of partial calls, such that `stake_all`/`unstake_all`/`withdraw_all` semantics diverge from repeated `stake`/`unstake`/`withdraw` and leak value or trap dust?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `staking-pool/src/lib.rs` full-position methods versus partial-position methods and their shared internals
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Compare a one-shot full-position transition against the equivalent set of partial transitions while holding total capital and epoch timing constant.
- Invariant to test: Economically equivalent full and partial public paths must lead to the same total claimable value, unlock timing, and pool accounting state.
- Expected Immunefi impact: Balance manipulation
- Fast validation: Build paired simulations that differ only by using `staking-pool/src/lib.rs::stake()` versus the equivalent partial sequence; assert identical balances, share totals, and unlock epochs.
