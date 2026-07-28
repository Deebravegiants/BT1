# Q3999: Minimum-deposit underestimation in create_staking_pool with repeat different id

## Question
Can an unprivileged attacker or honest user use `create_staking_pool()` with many create attempts with different IDs but one shared payer when `MIN_ATTACHED_BALANCE` is just barely met, and end up in a path where the factory accepts the deposit even though downstream creation costs are higher, causing partial execution or trapped funds instead of a clean pre-check failure?

## Target
- File/function: `staking-pool-factory/src/lib.rs::create_staking_pool` and `staking-pool-factory/src/lib.rs::on_staking_pool_create` plus `staking-pool-factory/src/lib.rs::MIN_ATTACHED_BALANCE`, `create_staking_pool`, and refund-on-failure semantics
- Entrypoint: `staking-pool-factory/src/lib.rs::create_staking_pool()`
- Attacker controls: attached deposit, `staking_pool_id`, `owner_id`, `stake_public_key`, `reward_fee_fraction`, caller shape, and async retry timing; specifically many create attempts with different IDs but one shared payer
- Exploit idea: Stress the exact boundary where the factory says the deposit is enough but downstream account creation, code deployment, or initialization may consume more than anticipated.
- Invariant to test: The advertised minimum deposit must be sufficient for the full happy path or the transaction must fail without economic loss.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: Boundary test at and just above `MIN_ATTACHED_BALANCE`; assert that all successful accepts either complete fully or refund exactly.
