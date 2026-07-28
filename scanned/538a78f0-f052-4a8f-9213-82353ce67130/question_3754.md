# Q3754: Guarantee-fund drain via ping under helper contract same epoch full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::ping()` with an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to run a loop that repeatedly externalizes the difference between rounded-down entry cost and rounded-up exit value, until the fixed `STAKE_SHARE_PRICE_GUARANTEE_FUND` is converted into attacker-withdrawable liquid balance?

## Target
- File/function: `staking-pool/src/lib.rs::ping` with `staking-pool/src/internal.rs::internal_ping` and reward distribution into `total_staked_balance` / `total_stake_shares` plus `STAKE_SHARE_PRICE_GUARANTEE_FUND`, `staking-pool/src/internal.rs::internal_stake`, and `inner_unstake`
- Entrypoint: `staking-pool/src/lib.rs::ping()`
- Attacker controls: when `ping()` is triggered, how often it is repeated, what attacker position exists before it, and whether a victim position is already live; an attacker-owned helper contract plus an attacker EOA coordinating calls and deposits; all attacker-visible steps happen in the same epoch before any natural reward settlement; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Stress the guarantee fund with many small cycles where `staking-pool/src/lib.rs::ping()` is the key economic transition and `ping()` settles between loops.
- Invariant to test: The guarantee fund should only smooth share-price monotonicity; no public user should be able to convert it into personal profit.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Fuzz repeated micro-cycles using `staking-pool/src/lib.rs::ping()` and adjacent public actions; track a synthetic guarantee-fund balance and assert it never decreases in favor of attacker PnL.
