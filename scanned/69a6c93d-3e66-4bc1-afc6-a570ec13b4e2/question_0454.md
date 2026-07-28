# Q454: Rounding extraction via deposit_and_stake under two account unlock boundary full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::deposit_and_stake()` with two attacker EOAs alternating calls to compare split and merged positions, the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking, and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to keep crossing the rounded-down mint path and the rounded-up exit path in different directions, so the attacker realizes more liquid NEAR than principal plus pro-rata rewards and effectively extracts value from the pool's rounding buffer?

## Target
- File/function: `staking-pool/src/lib.rs::deposit_and_stake` with `staking-pool/src/internal.rs::internal_deposit`, `internal_stake`, and `internal_ping` plus `staking-pool/src/internal.rs::internal_stake`, `staking-pool/src/internal.rs::inner_unstake`, and the `num_shares_from_staked_amount_rounded_*` / `staked_amount_from_num_shares_rounded_*` helpers
- Entrypoint: `staking-pool/src/lib.rs::deposit_and_stake()`
- Attacker controls: attached deposit size, split across attacker accounts, follow-up unstake timing, and reward-settlement timing; two attacker EOAs alternating calls to compare split and merged positions; the key step is attempted exactly at the four-epoch unlock boundary after prior unstaking; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Drive a cycle through `deposit_and_stake()` as the share-minting step, then `unstake()/unstake_all()/withdraw()` or third-party `ping()` settlement so stake-share conversion pays rounded-down on entry but rounded-up on exit for the same economic position.
- Invariant to test: Across any public call sequence, attacker withdrawals plus remaining claimable balance must never exceed attacker principal plus fair rewards, and rounding must not create an externally extractable surplus.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Stateful test over `staking-pool/src/lib.rs::deposit_and_stake()` with two attacker EOAs alternating calls to compare split and merged positions; sweep near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge across repeated entry/exit loops and assert non-positive attacker PnL net of legitimate rewards.
