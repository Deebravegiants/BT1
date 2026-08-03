# Q0106: create_with_pool_id can break BondedPools / PoolMembers conservation

## Question
Can an unprivileged attacker call `create_with_pool_id` with crafted amounts, fees, or prices, IDs, hashes, nonces, or location fields so `BondedPools` and `PoolMembers` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::create_with_pool_id
- Entrypoint: signed extrinsic `create_with_pool_id`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `BondedPools`, `PoolMembers`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
