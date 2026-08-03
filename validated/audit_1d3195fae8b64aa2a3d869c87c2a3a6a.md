[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L1-27)
```text
/// Allow stakers and operators to enter a staking contract with reward sharing.
/// The main accounting logic in a staking contract consists of 2 parts:
/// 1. Tracks how much commission needs to be paid out to the operator. This is tracked with an increasing principal
/// amount that's updated every time the operator requests commission, the staker withdraws funds, or the staker
/// switches operators.
/// 2. Distributions of funds to operators (commissions) and stakers (stake withdrawals) use the shares model provided
/// by the pool_u64 to track shares that increase in price as the stake pool accumulates rewards.
///
/// Example flow:
/// 1. A staker creates a staking contract with an operator by calling create_staking_contract() with 100 coins of
/// initial stake and commission = 10%. This means the operator will receive 10% of any accumulated rewards. A new stake
/// pool will be created and hosted in a separate account that's controlled by the staking contract.
/// 2. The operator sets up a validator node and, once ready, joins the validator set by calling stake::join_validator_set
/// 3. After some time, the stake pool gains rewards and now has 150 coins.
/// 4. Operator can now call request_commission. 10% of (150 - 100) = 5 coins will be unlocked from the stake pool. The
/// staker's principal is now updated from 100 to 145 (150 coins - 5 coins of commission). The pending distribution pool
/// has 5 coins total and the operator owns all 5 shares of it.
/// 5. Some more time has passed. The pool now has 50 more coins in rewards and a total balance of 195. The operator
/// calls request_commission again. Since the previous 5 coins have now become withdrawable, it'll be deposited into the
/// operator's account first. Their new commission will be 10% of (195 coins - 145 principal) = 5 coins. Principal is
/// updated to be 190 (195 - 5). Pending distribution pool has 5 coins and operator owns all 5 shares.
/// 6. Staker calls unlock_stake to unlock 50 coins of stake, which gets added to the pending distribution pool. Based
/// on shares math, staker will be owning 50 shares and operator still owns 5 shares of the 55-coin pending distribution
/// pool.
/// 7. Some time passes and the 55 coins become fully withdrawable from the stake pool. Due to accumulated rewards, the
/// 55 coins become 70 coins. Calling distribute() distributes 6 coins to the operator and 64 coins to the validator.
module aptos_framework::staking_contract {
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L73-85)
```text
    struct StakingContract has store {
        // Recorded principal after the last commission distribution.
        // This is only used to calculate the commission the operator should be receiving.
        principal: u64,
        pool_address: address,
        // The stake pool's owner capability. This can be used to control funds in the stake pool.
        owner_cap: OwnerCapability,
        commission_percentage: u64,
        // Current distributions, including operator commission withdrawals and staker's partial withdrawals.
        distribution_pool: Pool,
        // Just in case we need the SignerCap for stake pool account in the future.
        signer_cap: SignerCapability
    }
```
