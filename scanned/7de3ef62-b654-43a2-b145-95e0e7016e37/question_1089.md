# Q1089: Guarantee-fund drain via stake under two account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::stake()` with two attacker EOAs alternating calls to compare split and merged positions and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to run a loop that repeatedly externalizes the difference between rounded-down entry cost and rounded-up exit value, until the fixed `STAKE_SHARE_PRICE_GUARANTEE_FUND` is converted into attacker-withdrawable liquid balance?

## Target
- File/function: `staking-pool/src/lib.rs::stake` with `staking-pool/src/internal.rs::internal_stake` plus `STAKE_SHARE_PRICE_GUARANTEE_FUND`, `staking-pool/src/internal.rs::internal_stake`, and `inner_unstake`
- Entrypoint: `staking-pool/src/lib.rs::stake()`
- Attacker controls: stake amount, pre-existing unstaked balance, number of attacker accounts, and call ordering around epoch changes; two attacker EOAs alternating calls to compare split and merged positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Stress the guarantee fund with many small cycles where `staking-pool/src/lib.rs::stake()` is the key economic transition and `ping()` settles between loops.
- Invariant to test: The guarantee fund should only smooth share-price monotonicity; no public user should be able to convert it into personal profit.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Fuzz repeated micro-cycles using `staking-pool/src/lib.rs::stake()` and adjacent public actions; track a synthetic guarantee-fund balance and assert it never decreases in favor of attacker PnL.
