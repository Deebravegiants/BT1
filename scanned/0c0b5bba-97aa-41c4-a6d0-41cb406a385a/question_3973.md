# Q3973: Account-ID collision or aliasing in create_staking_pool with near collision

## Question
Can an unprivileged attacker use `create_staking_pool()` with a `staking_pool_id` chosen to sit near account-ID validation edge cases to create a `staking_pool_account_id` that passes local validation but collides with, aliases, or is interpreted as a different logical pool name elsewhere, leading to unauthorized ownership or whitelist state for the wrong account?

## Target
- File/function: `staking-pool-factory/src/lib.rs::create_staking_pool` and `staking-pool-factory/src/lib.rs::on_staking_pool_create` plus `staking-pool-factory/src/lib.rs::create_staking_pool`, `staking_pool_account_ids`, and `env::is_valid_account_id`
- Entrypoint: `staking-pool-factory/src/lib.rs::create_staking_pool()`
- Attacker controls: attached deposit, `staking_pool_id`, `owner_id`, `stake_public_key`, `reward_fee_fraction`, caller shape, and async retry timing; specifically a `staking_pool_id` chosen to sit near account-ID validation edge cases
- Exploit idea: Probe edge-case account prefixes to see whether validation, set insertion, and later whitelist behavior disagree on which account is being created.
- Invariant to test: Every successful create path must bind one unique logical `staking_pool_id` to one unique on-chain account with no aliasing or shadowing.
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: Property test over edge-case prefixes and canonicalization assumptions; assert that all accepted IDs map injectively to one deployed account.
