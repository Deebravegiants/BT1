# Q2417: Guarantee-fund drain via unstake_all under many account same epoch dust threshold

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::unstake_all()` with sixteen attacker EOAs splitting the same total capital into many dust positions and dust-sized values near the smallest amount that still mints nonzero shares or changes rounding to run a loop that repeatedly externalizes the difference between rounded-down entry cost and rounded-up exit value, until the fixed `STAKE_SHARE_PRICE_GUARANTEE_FUND` is converted into attacker-withdrawable liquid balance?

## Target
- File/function: `staking-pool/src/lib.rs::unstake_all` with `staking-pool/src/internal.rs::inner_unstake` plus `STAKE_SHARE_PRICE_GUARANTEE_FUND`, `staking-pool/src/internal.rs::internal_stake`, and `inner_unstake`
- Entrypoint: `staking-pool/src/lib.rs::unstake_all()`
- Attacker controls: existing share balance, total-share state, reward timing, and whether the full exit leaves residual dust or excess liquid value; sixteen attacker EOAs splitting the same total capital into many dust positions; all attacker-visible steps happen in the same epoch before any natural reward settlement; dust-sized values near the smallest amount that still mints nonzero shares or changes rounding
- Exploit idea: Stress the guarantee fund with many small cycles where `staking-pool/src/lib.rs::unstake_all()` is the key economic transition and `ping()` settles between loops.
- Invariant to test: The guarantee fund should only smooth share-price monotonicity; no public user should be able to convert it into personal profit.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Fuzz repeated micro-cycles using `staking-pool/src/lib.rs::unstake_all()` and adjacent public actions; track a synthetic guarantee-fund balance and assert it never decreases in favor of attacker PnL.
