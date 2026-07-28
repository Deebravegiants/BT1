# Q2234: Rounding extraction via unstake_all under helper contract same epoch full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake_all()` with an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits, all attacker-visible steps happen in the same epoch before any natural reward settlement, and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to keep crossing the rounded-down mint path and the rounded-up exit path in different directions, so the attacker realizes more liquid NEAR than principal plus pro-rata rewards and effectively extracts value from the pool's rounding buffer?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `staking-pool/src/internal.rs::inner_unstake`, and the `num_shares_from_staked_amount_rounded_*` / `staked_amount_from_num_shares_rounded_*` helpers
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Drive a cycle through build stake with `deposit_and_stake()` or `stake_all()`, then use `unstake_all()` as the full exit step before delayed `withdraw_all()` so stake-share conversion pays rounded-down on entry but rounded-up on exit for the same economic position.
- Invariant to test: Across any public call sequence, attacker withdrawals plus remaining claimable balance must never exceed attacker principal plus fair rewards, and rounding must not create an externally extractable surplus.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Stateful test over `staking-pool/src/lib.rs::unstake_all()` with an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; sweep near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge across repeated entry/exit loops and assert non-positive attacker PnL net of legitimate rewards.
