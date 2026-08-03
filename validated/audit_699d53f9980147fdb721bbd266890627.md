No vulnerability found for this question.

**Analysis:** `validate_high_txn_limits` calls `stake::is_current_epoch_validator(pool_address)` synchronously within the same prologue execution, immediately before granting the gas-limit multiplier [1](#0-0) . There is no cached or stale `pool_address`/membership state carried across an epoch boundary within this function — the check reads live validator-set membership at call time for all three request variants (`StakePoolOwner`, `DelegatedVoter`, `DelegationPoolDelegator`) [2](#0-1) . Since epoch transitions are atomic (they happen between transactions, not mid-transaction), there is no window within a single prologue invocation where `is_current_epoch_validator` can toggle from true to false after being checked.

More fundamentally, this module governs gas-limit multipliers for transaction execution/IO, not any asset custody surface — it never touches ownership refs, freeze capabilities, metadata authority, dispatchable hooks, or code-object ownership as required by the review's custody scope [3](#0-2) . Existing tests already assert rejection when a pool is not in the validator set (`test_validate_stake_pool_owner_pool_not_in_validator_set`, `test_validate_delegated_voter_pool_not_in_validator_set`, `test_validate_delegation_pool_delegator_pool_not_in_validator_set`), confirming the check functions as intended [4](#0-3) .

### Citations

**File:** aptos-move/framework/aptos-framework/sources/transaction_limits.move (L1-17)
```text
/// Manages configuration and validation for higher transaction limits based on
/// staking.
///
/// Users can request multipliers to transaction limits (e..g, execution limit
/// or IO limit) if they prove they control a significant stake in a stake pool
/// that is currently in the active validator set:
///   - as a stake pool owner,
///   - as a delegated voter,
///   - as a delegation pool delegator.
/// For example, one can request 2.5x on execution limits and 5x on IO limits.
///
/// Multipliers are expressed as percent of the base limit where 100 is 1x,
/// 250 is 2.5x.
///
/// The on-chain config stores a vector of tiers. Each tier maps multiplier to
/// the required minimum stake threshold. A smallest multiplier that is greater
/// than or equal to the requested multiplier is chosen.
```

**File:** aptos-move/framework/aptos-framework/sources/transaction_limits.move (L273-279)
```text
                let pool_address = stake::get_pool_address_for_owner(fee_payer);
                assert!(
                    stake::is_current_epoch_validator(pool_address),
                    error::permission_denied(EPOOL_NOT_IN_VALIDATOR_SET)
                );
                let stake_amount = aptos_governance::get_voting_power(pool_address);
                validate_enough_stake(stake_amount, multipliers);
```

**File:** aptos-move/framework/aptos-framework/sources/transaction_limits.move (L281-309)
```text
            DelegatedVoter { pool_address, multipliers } => {
                assert!(
                    stake::stake_pool_exists(pool_address),
                    error::not_found(ESTAKE_POOL_NOT_FOUND)
                );
                assert!(
                    fee_payer == stake::get_delegated_voter(pool_address),
                    error::permission_denied(ENOT_DELEGATED_VOTER)
                );
                assert!(
                    stake::is_current_epoch_validator(pool_address),
                    error::permission_denied(EPOOL_NOT_IN_VALIDATOR_SET)
                );
                let stake_amount = aptos_governance::get_voting_power(pool_address);
                validate_enough_stake(stake_amount, multipliers);
            },
            DelegationPoolDelegator { pool_address, multipliers } => {
                assert!(
                    delegation_pool::delegation_pool_exists(pool_address),
                    error::not_found(EDELEGATION_POOL_NOT_FOUND)
                );
                assert!(
                    stake::is_current_epoch_validator(pool_address),
                    error::permission_denied(EPOOL_NOT_IN_VALIDATOR_SET)
                );
                let (active, _, pending_inactive) = delegation_pool::get_stake(
                    pool_address, fee_payer
                );
                validate_enough_stake(active + pending_inactive, multipliers);
```

**File:** aptos-move/framework/aptos-framework/sources/transaction_limits.move (L765-823)
```text
    #[test(aptos_framework = @aptos_framework, validator = @0x123)]
    #[expected_failure(abort_code = 0x50009)]
    fun test_validate_stake_pool_owner_pool_not_in_validator_set(
        aptos_framework: &signer, validator: &signer
    ) {
        // Stake pool has plenty of APT but never joined the validator set.
        initialize_for_test_with_inactive_stake_pool(aptos_framework, validator, 1000);
        validate_high_txn_limits(
            @0x123,
            UserTxnLimitsRequest::StakePoolOwner {
                multipliers: RequestedMultipliers::V1 {
                    execution_multiplier_percent: 200,
                    io_multiplier_percent: 200
                }
            }
        );
    }

    #[test(aptos_framework = @aptos_framework, validator = @0x123)]
    #[expected_failure(abort_code = 0x50009)]
    fun test_validate_delegated_voter_pool_not_in_validator_set(
        aptos_framework: &signer, validator: &signer
    ) {
        initialize_for_test_with_inactive_stake_pool(aptos_framework, validator, 1000);
        stake::set_delegated_voter(validator, @0x456);
        validate_high_txn_limits(
            @0x456,
            UserTxnLimitsRequest::DelegatedVoter {
                pool_address: @0x123,
                multipliers: RequestedMultipliers::V1 {
                    execution_multiplier_percent: 200,
                    io_multiplier_percent: 200
                }
            }
        );
    }

    #[test(aptos_framework = @aptos_framework, pool_owner = @0x111, delegator = @0x222)]
    #[expected_failure(abort_code = 0x50009)]
    fun test_validate_delegation_pool_delegator_pool_not_in_validator_set(
        aptos_framework: &signer, pool_owner: &signer, delegator: &signer
    ) {
        initialize_for_test_with_inactive_delegation_pool(
            aptos_framework,
            pool_owner,
            delegator,
            20_0000_0000
        );
        validate_high_txn_limits(
            @0x222,
            UserTxnLimitsRequest::DelegationPoolDelegator {
                pool_address: delegation_pool::get_owned_pool_address(@0x111),
                multipliers: RequestedMultipliers::V1 {
                    execution_multiplier_percent: 200,
                    io_multiplier_percent: 200
                }
            }
        );
    }
```
