### Title
`estimate_minimal_gas_vector` Omits Fixed `gas_per_proof` Cost for Client-Side Proving Transactions, Causing Gateway to Admit Transactions That Will Inevitably Revert - (File: `crates/blockifier/src/fee/gas_usage.rs`)

### Summary

`estimate_minimal_gas_vector` is used in `check_fee_bounds` to gate gateway/mempool admission of transactions. For Invoke V3 transactions carrying `proof_facts`, the function correctly accounts for the per-felt archival cost of `proof_facts` (via `extended_calldata_length`) but silently omits the fixed `gas_per_proof` overhead (75,000,000 L2 gas in current versioned constants). The actual gas accounting path (`ArchivalDataResources::get_client_side_proof_gas_cost`) does charge this fixed cost. The result is that any transaction whose `max_l2_gas` falls in the gap `[estimate_minimal_gas_vector.l2_gas, estimate_minimal_gas_vector.l2_gas + gas_per_proof)` passes `check_fee_bounds` and is admitted, but then inevitably reverts during execution with an out-of-gas error while still consuming fees.

### Finding Description

**Admission path:**

`perform_pre_validation_stage` calls `check_fee_bounds`, which calls `estimate_minimal_gas_vector`: [1](#0-0) 

`estimate_minimal_gas_vector` computes OS steps using `extended_calldata_length()` (which includes `proof_facts_length()`), then converts to gas. It returns only DA gas + VM resources cost: [2](#0-1) 

`extended_calldata_length()` is defined as `calldata_length + proof_facts_length()`: [3](#0-2) 

**Actual gas accounting path:**

`TransactionReceipt::from_account_tx` passes `has_client_side_proof: account_tx.has_client_side_proof()` to `StarknetResources::new`: [4](#0-3) 

`ArchivalDataResources::to_gas_vector` calls `get_client_side_proof_gas_cost`, which adds the fixed `gas_per_proof` when `has_client_side_proof` is true: [5](#0-4) 

The fixed cost is `archival_gas_costs.gas_per_proof` = **75,000,000 L2 gas** in the current versioned constants: [6](#0-5) 

**The gap:** `estimate_minimal_gas_vector` returns a value that is `gas_per_proof` (75,000,000 L2 gas) lower than the actual minimum gas required for any transaction with non-empty `proof_facts`. The `check_fee_bounds` comparison: [7](#0-6) 

...passes for any `max_l2_gas` ≥ the underestimated minimum, even though the actual execution will charge an additional 75,000,000 L2 gas.

**Test evidence confirming the gap:** The test suite explicitly compensates for this by manually adding `proof_gas_cost` to resource bounds when testing with `proof_facts`, precisely because the estimate does not include it: [8](#0-7) 

### Impact Explanation

A user (or an attacker targeting a user's transaction) who sets `max_l2_gas` to exactly `estimate_minimal_gas_vector.l2_gas` for a transaction with `proof_facts` will:
1. Pass `check_fee_bounds` — the gateway/mempool admits the transaction.
2. Fail during execution with an out-of-gas error — the actual gas cost exceeds `max_l2_gas` by up to 75,000,000 L2 gas.
3. Still pay fees for the failed transaction.

This matches the **High** impact category: "Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing." The gateway admits transactions that are structurally guaranteed to revert, causing economic loss to users who rely on the sequencer's own fee estimation to set their resource bounds.

### Likelihood Explanation

- Any Invoke V3 transaction with non-empty `proof_facts` and `max_l2_gas` set to the value returned by `estimate_minimal_gas_vector` triggers this.
- The gateway's stateless validator enforces `max_calldata_length` (5000 felts) and `max_proof_size` (480,000 bytes), so `proof_facts` is bounded but the fixed `gas_per_proof` cost is independent of size.
- Users relying on the sequencer's own fee estimation API to set resource bounds are directly affected.
- The gap is large (75,000,000 L2 gas) relative to the per-felt cost (5,120 L2 gas/felt × 5,000 felts = 25,600,000 L2 gas maximum per-felt cost), meaning the fixed cost dominates and the underestimation is severe.

### Recommendation

Add the fixed `gas_per_proof` cost to `estimate_minimal_gas_vector` when the transaction has client-side proof facts:

```rust
// In estimate_minimal_gas_vector, after computing vm_resources_cost:
let proof_gas_cost = if tx.has_client_side_proof() {
    let archival_gas_costs = versioned_constants
        .get_archival_data_gas_costs(gas_usage_vector_computation_mode);
    GasVector::from_l2_gas(archival_gas_costs.gas_per_proof.to_integer().into())
} else {
    GasVector::ZERO
};
da_gas_cost
    .checked_add(vm_resources_cost)
    .and_then(|v| v.checked_add(proof_gas_cost))
    ...
```

Alternatively, refactor `estimate_minimal_gas_vector` to reuse `StarknetResources::new` + `ArchivalDataResources::to_gas_vector` directly, eliminating the divergence between the estimation path and the actual accounting path.

### Proof of Concept

1. Deploy an Invoke V3 account on a node running the current versioned constants (`gas_per_proof = 75_000_000`).
2. Construct an Invoke V3 transaction with valid `proof_facts` (non-empty).
3. Call `estimate_minimal_gas_vector` (or the equivalent RPC fee estimation endpoint) to obtain `min_l2_gas`.
4. Submit the transaction with `max_l2_gas = min_l2_gas` (exactly the estimated minimum).
5. Observe: `check_fee_bounds` passes (gateway admits the transaction).
6. Observe: execution reverts with out-of-gas because the actual L2 gas cost is `min_l2_gas + 75_000_000`.
7. Observe: the user is charged fees for the reverted transaction.

The 75,000,000 L2 gas gap is confirmed by the test at: [9](#0-8) 

which explicitly adds `proof_gas_cost` to the resource bounds to make the transaction succeed — a workaround that would be unnecessary if `estimate_minimal_gas_vector` were correct.

### Citations

**File:** crates/blockifier/src/transaction/account_transaction.rs (L202-206)
```rust
    /// Returns the total calldata length, including proof_facts.
    /// Both are charged at the same gas per data felt rate.
    pub fn extended_calldata_length(&self) -> usize {
        self.calldata_length() + self.proof_facts_length()
    }
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L374-382)
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
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L427-458)
```rust
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

**File:** crates/blockifier/src/fee/gas_usage.rs (L156-214)
```rust
/// Returns an estimated lower bound for the gas required by the given account transaction.
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

**File:** crates/blockifier/src/fee/receipt.rs (L177-191)
```rust
        Self::from_params(TransactionReceiptParameters {
            tx_context,
            gas_mode: tx_context.get_gas_vector_computation_mode(),
            extended_calldata_length: account_tx.extended_calldata_length(),
            signature_length: account_tx.signature_length(),
            code_size: account_tx.declare_code_size(),
            state_changes,
            sender_address: Some(tx_context.tx_info.sender_address()),
            l1_handler_payload_size: None,
            execution_summary_without_fee_transfer,
            tx_type: account_tx.tx_type(),
            reverted_steps,
            reverted_sierra_gas,
            has_client_side_proof: account_tx.has_client_side_proof(),
        })
```

**File:** crates/blockifier/src/fee/resources.rs (L338-362)
```rust
    fn get_client_side_proof_gas_cost(
        &self,
        versioned_constants: &VersionedConstants,
        mode: &GasVectorComputationMode,
    ) -> GasVector {
        if !self.has_client_side_proof {
            return GasVector::ZERO;
        }

        let archival_gas_costs = versioned_constants.get_archival_data_gas_costs(mode);

        // Client-side proofs have a fixed gas cost. This cost corresponds to the
        // current proof version (reflected in the first proof fact).
        let proof_gas: GasAmount = archival_gas_costs.gas_per_proof.to_integer().into();

        match mode {
            GasVectorComputationMode::All => GasVector::from_l2_gas(proof_gas),
            GasVectorComputationMode::NoL2Gas => {
                unreachable!(
                    "Client side proving is only supported from V3 transactions, which use \
                     AllResourceBounds."
                )
            }
        }
    }
```

**File:** crates/blockifier/resources/blockifier_versioned_constants_0_14_4.json (L46-49)
```json
        "gas_per_proof": [
            75000000,
            1
        ]
```

**File:** crates/blockifier/src/transaction/transactions_test.rs (L619-641)
```rust
    let resource_bounds = if proof_facts.is_empty() {
        resource_bounds
    } else {
        match resource_bounds {
            ValidResourceBounds::AllResources(all_bounds) => {
                // For client-side proving transactions, reserve extra L2 gas for the fixed proof
                // cost.
                let proof_gas_cost: u64 =
                    versioned_constants.archival_data_gas_costs.gas_per_proof.to_integer();

                ValidResourceBounds::AllResources(AllResourceBounds {
                    l2_gas: ResourceBounds {
                        max_amount: GasAmount(all_bounds.l2_gas.max_amount.0 + proof_gas_cost),
                        ..all_bounds.l2_gas
                    },
                    ..all_bounds
                })
            }
            // Skip impossible combination: proof_facts only exist in V3 transactions,
            // and V3 uses AllResourceBounds (L1Gas is legacy-only).
            ValidResourceBounds::L1Gas(_) => return,
        }
    };
```
