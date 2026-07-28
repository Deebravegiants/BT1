# Q208: Guarantee-fund drain via deposit under single account ping heavy full position edge

## Question
Can an unprivileged attacker use `staking-pool/src/lib.rs::deposit()` with one attacker EOA controlling a single staking position and near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge to run a loop that repeatedly externalizes the difference between rounded-down entry cost and rounded-up exit value, until the fixed `STAKE_SHARE_PRICE_GUARANTEE_FUND` is converted into attacker-withdrawable liquid balance?

## Target
- File/function: `staking-pool/src/lib.rs::deposit` with `staking-pool/src/internal.rs::internal_deposit` and `staking-pool/src/internal.rs::internal_ping` plus `STAKE_SHARE_PRICE_GUARANTEE_FUND`, `staking-pool/src/internal.rs::internal_stake`, and `inner_unstake`
- Entrypoint: `staking-pool/src/lib.rs::deposit()`
- Attacker controls: attached deposit size, number of attacker accounts, follow-up call ordering, and epoch timing; one attacker EOA controlling a single staking position; a third party or attacker-owned helper repeatedly inserts public `ping()` calls between every economic step; near-full-position amounts that leave, consume, or depend on a one-yocto residual balance/share edge
- Exploit idea: Stress the guarantee fund with many small cycles where `staking-pool/src/lib.rs::deposit()` is the key economic transition and `ping()` settles between loops.
- Invariant to test: The guarantee fund should only smooth share-price monotonicity; no public user should be able to convert it into personal profit.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Fuzz repeated micro-cycles using `staking-pool/src/lib.rs::deposit()` and adjacent public actions; track a synthetic guarantee-fund balance and assert it never decreases in favor of attacker PnL.
