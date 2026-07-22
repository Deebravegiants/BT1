### Title
`estimate_minimal_gas_vector` Omits Archival-Data (Calldata + Signature) Gas Cost from Pre-Validation Bound Check — (`File: crates/blockifier/src/fee/gas_usage.rs`)

### Summary

`estimate_minimal_gas_vector` is used in `check_fee_bounds` to enforce that a transaction's declared resource bounds are at least as large as the minimum cost the sequencer will charge. The function computes only DA gas and VM-step (OS overhead) gas, but omits the archival-data gas component — the per-felt cost for calldata and signature storage — that the actual `TransactionReceipt` computation always includes. A user can therefore submit a V3 transaction whose `l2_gas.max_amount` (or `l1_gas.max_amount` for legacy bounds) is set exactly to the underestimated minimum, pass pre-validation, and then have the transaction reverted post-execution because the real cost exceeds the declared bound. The sequencer charges only the declared bound, not the true cost, so it is systematically under-compensated for the archival-data work it performed.

### Finding Description

`estimate_minimal_gas_vector` in `crates/blockifier/src/fee/gas_usage.rs` (lines 157–214) returns only two components:

1. `da_gas_cost` — DA gas for the expected state changes
2. `vm_resources_cost` — L1/L2 gas for the OS-overhead steps [1](#0-0) 

The actual per-transaction cost, computed in `TransactionResources::to_gas_vector`, additionally includes `StarknetResources::to_gas_vector`, which calls `ArchivalDataResources::to_gas_vector`. That function adds:

- `get_calldata_and_signature_gas_cost` — `gas_per_data_felt × (calldata_length + signature_length)` in L2 gas (for `AllResourceBounds`) or L1 gas (for `L1Gas` bounds)
- `get_code_gas_cost` — for Declare transactions
- event emission costs [2](#0-1) 

`check_fee_bounds` calls `estimate_minimal_gas_vector` and rejects the transaction only if `minimal_gas_amount > resource_bounds.max_amount`: [3](#0-2) 

Because the archival-data component is absent from the estimate, a transaction whose declared bound equals the underestimated minimum passes this check even though the actual cost will exceed the bound.

The TODO comment in the function itself acknowledges the incompleteness: [4](#0-3) 

### Impact Explanation

For a V3 transaction using `AllResourceBounds` (`GasVectorComputationMode::All`), `archival_data_gas_costs.gas_per_data_felt` is `5120` L2 gas per felt. With the gateway's `max_calldata_length` of 5000 felts, the missing archival-data component is up to `5000 × 5120 = 25,600,000 L2 gas` per transaction. An attacker sets `l2_gas.max_amount` to exactly the underestimated minimum, passes pre-validation, triggers a post-execution revert (actual cost > bound), and is charged only the declared bound. The sequencer processes and stores the full calldata but is compensated only for the OS-step and DA components. This is a direct, repeatable economic loss to the sequencer with no privilege required. [5](#0-4) 

### Likelihood Explanation

Any unprivileged user can craft a V3 `InvokeTransaction` with maximum calldata and set `l2_gas.max_amount` to the value returned by `estimate_minimal_gas_vector`. The gateway's `max_calldata_length` limit (5000 felts) is the only bound on the per-transaction loss. The attack is deterministic and requires no special knowledge beyond the public versioned-constants values. [6](#0-5) 

### Recommendation

Refactor `estimate_minimal_gas_vector` to include the archival-data gas cost, consistent with the existing TODO:

```
// TODO(Yoni): BLOCKIFIER-RESET: reuse TransactionReceipt code.
```

Concretely, after computing `da_gas_cost` and `vm_resources_cost`, also compute and add the calldata/signature archival-data cost using `ArchivalDataResources::get_calldata_and_signature_gas_cost` (or by constructing a `StarknetResources` and calling `to_gas_vector`), so that `check_fee_bounds` rejects any transaction whose declared bounds cannot cover the full minimum cost. [5](#0-4) 

### Proof of Concept

1. Read `archival_data_gas_costs.gas_per_data_felt` from the active `VersionedConstants` (e.g., `5120` in `blockifier_versioned_constants_0_14_4.json`).
2. Call `estimate_minimal_gas_vector` for a V3 Invoke with 5000-felt calldata; record the returned `l2_gas` value `M`.
3. Submit a V3 `InvokeTransaction` with `l2_gas.max_amount = M` and 5000 felts of calldata.
4. Observe: pre-validation passes (`M >= M`).
5. Observe: post-execution reverts because actual L2 gas = `M + 5000 × 5120 = M + 25,600,000 > M`.
6. Observe: the sequencer charges only `M × l2_gas_price` instead of `(M + 25,600,000) × l2_gas_price`. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/blockifier/src/fee/gas_usage.rs (L157-214)
```rust
pub fn estimate_minimal_gas_vector(
    block_context: &BlockContext,
    tx: &AccountTransaction,
    gas_usage_vector_computation_mode: &GasVectorComputationMode,
) -> GasVector {
    // TODO(Dori, 1/8/2023): Give names to the constant VM step estimates and regression-test them.
    let BlockContext { block_info, versioned_constants, .. } = block_context;
    let state_changes_by_account_tx = match &tx.tx {
        // We consider the following state changes: sender balance update (storage update) + nonce
        // increment (contract modification) (we exclude the sequencer balance update and the ERC20
        // contract modification since it occurs for every tx).
        Transaction::Declare(_) => StateChangesCount {
            n_storage_updates: 1,
            n_class_hash_updates: 0,
            // TODO(Yoni): BLOCKIFIER-RESET: should be 1.
            n_compiled_class_hash_updates: 0,
            n_modified_contracts: 1,
        },
        Transaction::Invoke(_) => StateChangesCount {
            n_storage_updates: 1,
            n_class_hash_updates: 0,
            n_compiled_class_hash_updates: 0,
            n_modified_contracts: 1,
        },
        // DeployAccount also updates the address -> class hash mapping.
        Transaction::DeployAccount(_) => StateChangesCount {
            n_storage_updates: 1,
            n_class_hash_updates: 1,
            n_compiled_class_hash_updates: 0,
            n_modified_contracts: 1,
        },
    };

    // TODO(Yoni): BLOCKIFIER-RESET: reuse TransactionReceipt code.
    let data_segment_length = get_onchain_data_segment_length(&state_changes_by_account_tx);
    let os_steps_for_type = versioned_constants
        .os_resources_for_tx_type(&tx.tx_type(), tx.extended_calldata_length())
        .n_steps
        + versioned_constants.os_kzg_da_resources(data_segment_length).n_steps;

    let resources = ExtendedExecutionResources {
        vm_resources: ExecutionResources { n_steps: os_steps_for_type, ..Default::default() },
        ..Default::default()
    };
    let da_gas_cost = get_da_gas_cost(&state_changes_by_account_tx, block_info.use_kzg_da);
    let vm_resources_cost = get_extended_vm_resources_cost(
        versioned_constants,
        &resources,
        0,
        gas_usage_vector_computation_mode,
    );
    da_gas_cost.checked_add(vm_resources_cost).unwrap_or_else(|| {
        panic!(
            "Overflow in minimal gas estimation; attempted to add {da_gas_cost:?} to \
             {vm_resources_cost:?}"
        )
    })
}
```

**File:** crates/blockifier/src/fee/resources.rs (L271-315)
```rust
impl ArchivalDataResources {
    /// Returns the cost of the transaction's archival data, for example, calldata, signature, code,
    /// and events.
    pub fn to_gas_vector(
        &self,
        versioned_constants: &VersionedConstants,
        mode: &GasVectorComputationMode,
    ) -> GasVector {
        [
            self.get_calldata_and_signature_gas_cost(versioned_constants, mode),
            self.get_code_gas_cost(versioned_constants, mode),
            self.get_client_side_proof_gas_cost(versioned_constants, mode),
            self.event_summary.to_gas_vector(versioned_constants, mode),
        ]
        .into_iter()
        .fold(GasVector::ZERO, |accumulator, cost| {
            accumulator.checked_add(cost).unwrap_or_else(|| {
                panic!(
                    "Archival data resources to gas vector overflowed: tried to add \
                     {accumulator:?} gas vector to {cost:?} gas vector.",
                )
            })
        })
    }

    /// Returns the cost for transaction calldata and transaction signature. Each felt costs a
    /// fixed and configurable amount of gas. This cost represents the cost of storing the
    /// calldata and the signature on L2.
    fn get_calldata_and_signature_gas_cost(
        &self,
        versioned_constants: &VersionedConstants,
        mode: &GasVectorComputationMode,
    ) -> GasVector {
        let archival_gas_costs = versioned_constants.get_archival_data_gas_costs(mode);

        // TODO(Avi, 20/2/2024): Calculate the number of bytes instead of the number of felts.
        let total_data_size = u64_from_usize(self.extended_calldata_length + self.signature_length);
        let gas_amount =
            (archival_gas_costs.gas_per_data_felt * total_data_size).to_integer().into();

        match mode {
            GasVectorComputationMode::All => GasVector::from_l2_gas(gas_amount),
            GasVectorComputationMode::NoL2Gas => GasVector::from_l1_gas(gas_amount),
        }
    }
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L374-458)
```rust
    fn check_fee_bounds(
        &self,
        tx_context: &TransactionContext,
    ) -> TransactionPreValidationResult<()> {
        let minimal_gas_amount_vector = estimate_minimal_gas_vector(
            &tx_context.block_context,
            self,
            &tx_context.get_gas_vector_computation_mode(),
        );
        let TransactionContext { block_context, tx_info } = tx_context;
        let block_info = &block_context.block_info;
        let fee_type = &tx_info.fee_type();
        match tx_info {
            TransactionInfo::Current(context) => {
                let resources_amount_tuple = match &context.resource_bounds {
                    ValidResourceBounds::L1Gas(l1_gas_resource_bounds) => vec![(
                        L1Gas,
                        l1_gas_resource_bounds,
                        minimal_gas_amount_vector.to_l1_gas_for_fee(
                            tx_context.get_gas_prices(),
                            &tx_context.block_context.versioned_constants,
                        ),
                        block_info.gas_prices.l1_gas_price(fee_type),
                    )],
                    ValidResourceBounds::AllResources(AllResourceBounds {
                        l1_gas: l1_gas_resource_bounds,
                        l2_gas: l2_gas_resource_bounds,
                        l1_data_gas: l1_data_gas_resource_bounds,
                    }) => {
                        let GasPriceVector { l1_gas_price, l1_data_gas_price, l2_gas_price } =
                            block_info.gas_prices.gas_price_vector(fee_type);
                        vec![
                            (
                                L1Gas,
                                l1_gas_resource_bounds,
                                minimal_gas_amount_vector.l1_gas,
                                *l1_gas_price,
                            ),
                            (
                                L1DataGas,
                                l1_data_gas_resource_bounds,
                                minimal_gas_amount_vector.l1_data_gas,
                                *l1_data_gas_price,
                            ),
                            (
                                L2Gas,
                                l2_gas_resource_bounds,
                                minimal_gas_amount_vector.l2_gas,
                                *l2_gas_price,
                            ),
                        ]
                    }
                };
                let insufficiencies = resources_amount_tuple
                    .iter()
                    .flat_map(
                        |(resource, resource_bounds, minimal_gas_amount, actual_gas_price)| {
                            let mut insufficiencies_resource = vec![];
                            if minimal_gas_amount > &resource_bounds.max_amount {
                                insufficiencies_resource.push(
                                    ResourceBoundsError::MaxGasAmountTooLow {
                                        resource: *resource,
                                        max_gas_amount: resource_bounds.max_amount,
                                        minimal_gas_amount: *minimal_gas_amount,
                                    },
                                );
                            }
                            if resource_bounds.max_price_per_unit < actual_gas_price.get() {
                                insufficiencies_resource.push(
                                    ResourceBoundsError::MaxGasPriceTooLow {
                                        resource: *resource,
                                        max_gas_price: resource_bounds.max_price_per_unit,
                                        actual_gas_price: (*actual_gas_price).into(),
                                    },
                                );
                            }
                            insufficiencies_resource
                        },
                    )
                    .collect::<Vec<_>>();
                if !insufficiencies.is_empty() {
                    return Err(Box::new(TransactionFeeError::InsufficientResourceBounds {
                        errors: insufficiencies,
                    }))?;
                }
```
