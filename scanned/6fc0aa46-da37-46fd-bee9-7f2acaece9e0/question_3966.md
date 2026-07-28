# Q3966: Refund binding mismatch in create_staking_pool with repeat same id

## Question
Can an unprivileged attacker use `staking-pool-factory/src/lib.rs::create_staking_pool()` with two back-to-back create attempts for the same `staking_pool_id` to make the failure-path refund go to the wrong account because `predecessor_account_id` is snapshotted before the async create/deploy/init sequence completes?

## Target
- File/function: `staking-pool-factory/src/lib.rs::create_staking_pool` and `staking-pool-factory/src/lib.rs::on_staking_pool_create` plus `staking-pool-factory/src/lib.rs::create_staking_pool` and `on_staking_pool_create`
- Entrypoint: `staking-pool-factory/src/lib.rs::create_staking_pool()`
- Attacker controls: attached deposit, `staking_pool_id`, `owner_id`, `stake_public_key`, `reward_fee_fraction`, caller shape, and async retry timing; specifically two back-to-back create attempts for the same `staking_pool_id`
- Exploit idea: Force initialization rollback after the factory has already accepted the deposit and verify that the exact attached value returns only to the economically correct payer.
- Invariant to test: On failure, the full attached deposit must be refunded to the rightful payer and never become claimable by an attacker-controlled intermediary.
- Expected Immunefi impact: Stealing or loss of funds
- Fast validation: near-sdk-sim test that forces pool initialization failure through malformed downstream state and asserts exact refund destination and amount.
