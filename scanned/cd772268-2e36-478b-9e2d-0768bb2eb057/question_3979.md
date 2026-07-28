# Q3979: Rollback tracking desync in create_staking_pool with helper forwarder

## Question
Can an unprivileged attacker use `create_staking_pool()` with an attacker-owned helper contract forwarding the create call on behalf of an EOA to force a partial-failure path where `staking_pool_account_ids` is updated in one direction but not restored in the other, leaving the factory permanently believing an ID exists or does not exist incorrectly?

## Target
- File/function: `staking-pool-factory/src/lib.rs::create_staking_pool` and `staking-pool-factory/src/lib.rs::on_staking_pool_create` plus `staking-pool-factory/src/lib.rs::create_staking_pool`, `staking_pool_account_ids.insert`, and callback rollback removal
- Entrypoint: `staking-pool-factory/src/lib.rs::create_staking_pool()`
- Attacker controls: attached deposit, `staking_pool_id`, `owner_id`, `stake_public_key`, `reward_fee_fraction`, caller shape, and async retry timing; specifically an attacker-owned helper contract forwarding the create call on behalf of an EOA
- Exploit idea: Target the exact window between optimistic set insertion and asynchronous callback cleanup after failed deployment or initialization.
- Invariant to test: The factory's internal registry must stay exactly synchronized with what was actually deployed and initialized on-chain.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Simulate failing create/deploy/init paths and immediately retry with the same ID; assert registry state matches deployability every time.
