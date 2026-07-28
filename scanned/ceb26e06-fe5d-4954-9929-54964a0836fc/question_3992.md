# Q3992: Whitelist atomicity gap in create_staking_pool with whitelist failure path

## Question
Can an unprivileged attacker use `create_staking_pool()` with a case where pool creation succeeds but the downstream whitelist step is the risky edge so pool deployment succeeds but whitelist insertion fails or diverges silently, leaving a user-funded pool in an inconsistent state where value is committed but the intended admission guarantee is broken?

## Target
- File/function: `staking-pool-factory/src/lib.rs::create_staking_pool` and `staking-pool-factory/src/lib.rs::on_staking_pool_create` plus `staking-pool-factory/src/lib.rs::on_staking_pool_create` and the downstream whitelist promise
- Entrypoint: `staking-pool-factory/src/lib.rs::create_staking_pool()`
- Attacker controls: attached deposit, `staking_pool_id`, `owner_id`, `stake_public_key`, `reward_fee_fraction`, caller shape, and async retry timing; specifically a case where pool creation succeeds but the downstream whitelist step is the risky edge
- Exploit idea: Treat successful deployment plus failed whitelist as an atomicity problem and test whether the factory leaves users with a half-completed economic result.
- Invariant to test: User-funded pool creation should either produce a usable, correctly whitelisted pool or cleanly roll back economic expectations without trapping value.
- Expected Immunefi impact: Contracts execution flows
- Fast validation: Mock a whitelist failure after successful pool creation and assert no silent success path leaves a funded but logically unusable pool.
