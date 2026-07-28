# Q2641: Rounding extraction via withdraw under single account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::withdraw()` with one attacker EOA controlling a single staking position, all attacker-visible steps happen in the same epoch before any natural reward settlement, and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to keep crossing the rounded-down mint path and the rounded-up exit path in different directions, so the attacker realizes more liquid NEAR than principal plus pro-rata rewards and effectively extracts value from the pool's rounding buffer?

## Target
- File/function: `staking-pool/src/lib.rs::withdraw` with `staking-pool/src/internal.rs::internal_withdraw` and `internal_ping` plus `staking-pool/src/internal.rs::internal_stake`, `staking-pool/src/internal.rs::inner_unstake`, and the `num_shares_from_staked_amount_rounded_*` / `staked_amount_from_num_shares_rounded_*` helpers
- Entrypoint: `staking-pool/src/lib.rs::withdraw()`
- Attacker controls: withdraw amount, unstake timing, epoch height, and any `ping()` calls inserted before withdrawal; one attacker EOA controlling a single staking position; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Drive a cycle through reach an unstaked balance through prior public calls, then use `withdraw()` as the value-extraction step so stake-share conversion pays rounded-down on entry but rounded-up on exit for the same economic position.
- Invariant to test: Across any public call sequence, attacker withdrawals plus remaining claimable balance must never exceed attacker principal plus fair rewards, and rounding must not create an externally extractable surplus.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Stateful test over `staking-pool/src/lib.rs::withdraw()` with one attacker EOA controlling a single staking position; sweep dust-sized values near the smallest amount that still mints nonzero shares or changes rounding across repeated entry/exit loops and assert non-positive attacker PnL net of legitimate rewards.
