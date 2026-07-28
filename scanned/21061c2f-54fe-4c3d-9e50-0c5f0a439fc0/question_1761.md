# Q1761: Rounding extraction via unstake under single account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake()` with one attacker EOA controlling a single staking position, all attacker-visible steps happen in the same epoch before any natural reward settlement, and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to keep crossing the rounded-down mint path and the rounded-up exit path in different directions, so the attacker realizes more liquid NEAR than principal plus pro-rata rewards and effectively extracts value from the pool's rounding buffer?

## Target
- File/function: `staking-pool/src/lib.rs::unstake` with `staking-pool/src/internal.rs::inner_unstake` plus `staking-pool/src/internal.rs::internal_stake`, `staking-pool/src/internal.rs::inner_unstake`, and the `num_shares_from_staked_amount_rounded_*` / `staked_amount_from_num_shares_rounded_*` helpers
- Entrypoint: `staking-pool/src/lib.rs::unstake()`
- Attacker controls: unstake amount, existing share balance, epoch boundary, and post-unstake withdrawal timing; one attacker EOA controlling a single staking position; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Drive a cycle through build stake with `deposit_and_stake()` or `stake()`, then use `unstake()` as the share-to-liquid step before delayed `withdraw()` so stake-share conversion pays rounded-down on entry but rounded-up on exit for the same economic position.
- Invariant to test: Across any public call sequence, attacker withdrawals plus remaining claimable balance must never exceed attacker principal plus fair rewards, and rounding must not create an externally extractable surplus.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Stateful test over `staking-pool/src/lib.rs::unstake()` with one attacker EOA controlling a single staking position; sweep dust-sized values near the smallest amount that still mints nonzero shares or changes rounding across repeated entry/exit loops and assert non-positive attacker PnL net of legitimate rewards.
