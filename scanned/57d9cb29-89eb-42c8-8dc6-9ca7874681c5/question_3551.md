# Q3551: Rounding extraction via ping under victim pair ping heavy dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::ping()` with one attacker EOA acting against a passive victim account that is already staked, a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step, and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to keep crossing the rounded-down mint path and the rounded-up exit path in different directions, so the attacker realizes more liquid NEAR than principal plus pro-rata rewards and effectively extracts value from the pool's rounding buffer?

## Target
- File/function: `staking-pool/src/lib.rs::ping` with `staking-pool/src/internal.rs::internal_ping` and reward distribution into `total_staked_balance` / `total_stake_shares` plus `staking-pool/src/internal.rs::internal_stake`, `staking-pool/src/internal.rs::inner_unstake`, and the `num_shares_from_staked_amount_rounded_*` / `staked_amount_from_num_shares_rounded_*` helpers
- Entrypoint: `staking-pool/src/lib.rs::ping()`
- Attacker controls: when `ping()` is triggered, how often it is repeated, what attacker position exists before it, and whether a victim position is already live; one attacker EOA acting against a passive victim account that is already staked; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Drive a cycle through use public `ping()` as the reward-settlement trigger between attacker-controlled deposit/stake/unstake/withdraw steps so stake-share conversion pays rounded-down on entry but rounded-up on exit for the same economic position.
- Invariant to test: Across any public call sequence, attacker withdrawals plus remaining claimable balance must never exceed attacker principal plus fair rewards, and rounding must not create an externally extractable surplus.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Stateful test over `staking-pool/src/lib.rs::ping()` with one attacker EOA acting against a passive victim account that is already staked; sweep dust-sized values near the smallest amount that still mints nonzero shares or changes rounding across repeated entry/exit loops and assert non-positive attacker PnL net of legitimate rewards.
