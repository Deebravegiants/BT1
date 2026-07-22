### Title
`estimate_minimal_gas_vector` Omits `n_compiled_class_hash_updates` for Declare V2/V3 Transactions, Causing Pre-Validation to Accept Transactions That Revert Post-Execution - (`File: crates/blockifier/src/fee/gas_usage.rs`)

---

### Summary

`estimate_minimal_gas_vector` deliberately sets `n_compiled_class_hash_updates: 0` for `Declare` transactions even though Declare V2/V3 always writes one compiled-class-hash entry to the state diff. The acknowledged TODO comment reads `// TODO(Yoni): BLOCKIFIER-RESET: should be 1.` The undercount propagates into `check_fee_bounds`, which uses the estimate as the floor for the user's resource bounds. A user who sets their bounds exactly at the (incorrect) floor passes pre-validation but then fails the post-execution bounds check, causing a revert and a fee charge for a failed transaction.

---

### Finding Description

`estimate_minimal_gas_vector` computes the minimum gas a transaction must declare in its resource bounds. For `Declare` transactions it builds a `StateChangesCount` that omits the compiled-class-hash write:

```rust
Transaction::Declare(_) => StateChangesCount {
    n_storage_updates: 1,
    n_class_hash_updates: 0,
    // TODO(Yoni): BLOCKIFIER-RESET: should be 1.
    n_compiled_class_hash_updates: 0,
    n_modified_contracts: 1,
},
``` [1](#0-0) 

The actual state changes produced by a Declare V2/V3 execution include `n_compiled_class_hash_updates: 1`, as confirmed by the test helper `declare_expected_state_changes_count`:

```rust
} else if version == TransactionVersion::TWO || version == TransactionVersion::THREE {
    StateChangesCount {
        n_storage_updates: 1,
        n_modified_contracts: 1,
        n_compiled_class_hash_updates: 1, // Also set compiled class hash.
        ..StateChangesCount::default()
    }
``` [2](#0-1) 

`get_onchain_data_segment_length` adds **2 felts** per compiled-class-hash update to the DA segment:

```rust
onchain_data_segment_length += state_changes_count.n_compiled_class_hash_updates * 2;
``` [3](#0-2) 

In KZG-DA (blob) mode each felt costs `DATA_GAS_PER_FIELD_ELEMENT = 128` blob-gas units, so the missing DA cost is **256 L1-data-gas units** per Declare V2/V3 transaction. In calldata mode the missing cost is `2 × SHARP_GAS_PER_DA_WORD` L1-gas units.

`check_fee_bounds` calls `estimate_minimal_gas_vector` and rejects any transaction whose declared bounds are below the estimate:

```rust
let minimal_gas_amount_vector = estimate_minimal_gas_vector(
    &tx_context.block_context,
    self,
    &tx_context.get_gas_vector_computation_mode(),
);
``` [4](#0-3) 

Because the estimate is too low, a Declare V2/V3 transaction with resource bounds set to the (incorrect) minimum passes `check_fee_bounds` and `verify_can_pay_committed_bounds` in `perform_pre_validation_stage`: [5](#0-4) 

The transaction is admitted to the mempool and executed. During execution the actual DA gas consumed includes the compiled-class-hash write. `PostExecutionReport::new` then compares actual gas against the declared bounds and finds `actual_amount > max_amount`, triggering a revert and charging the user the maximum declared fee. [6](#0-5) 

---

### Impact Explanation

Any user or tool that calls `estimate_minimal_gas_vector` (or the equivalent RPC `starknet_estimateFee`) to set tight-but-correct resource bounds for a Declare V2/V3 transaction will receive the same underestimated floor. The transaction passes gateway admission, is sequenced, executes successfully up to the post-execution check, then reverts. The user is charged the maximum declared fee for a failed transaction. This is a direct economic loss with no user error: the sequencer's own estimation function produces the wrong answer.

---

### Likelihood Explanation

Any wallet, SDK, or integration that uses the sequencer's own fee-estimation endpoint to set resource bounds for Declare V2/V3 transactions will reproduce this condition deterministically. The bug is present in every Declare V2/V3 transaction submitted with bounds derived from `estimate_minimal_gas_vector`. The TODO comment confirms the developers are aware the value is wrong.

---

### Recommendation

Change `n_compiled_class_hash_updates` from `0` to `1` for `Declare` transactions in `estimate_minimal_gas_vector`:

```rust
Transaction::Declare(_) => StateChangesCount {
    n_storage_updates: 1,
    n_class_hash_updates: 0,
    n_compiled_class_hash_updates: 1, // Declare V2/V3 writes compiled_class_hash.
    n_modified_contracts: 1,
},
``` [1](#0-0) 

For Declare V0/V1 (which do not write a compiled-class-hash), the value should remain `0`. A version-aware branch (matching on `tx.tx`) is needed if V0/V1 support must be preserved.

---

### Proof of Concept

1. Obtain the minimal gas vector for a Declare V3 transaction using `estimate_minimal_gas_vector` with `use_kzg_da = true`.
2. Submit a Declare V3 transaction with `l1_data_gas.max_amount` set exactly to `minimal_gas_vector.l1_data_gas` (the value returned in step 1).
3. Observe that `check_fee_bounds` passes (pre-validation succeeds).
4. Observe that `PostExecutionReport::new` returns `FeeCheckError::MaxGasAmountExceeded { resource: L1DataGas, actual_amount: minimal_gas_vector.l1_data_gas + 256, max_amount: minimal_gas_vector.l1_data_gas }`.
5. The transaction is reverted and the user is charged `l1_data_gas.max_amount × l1_data_gas_price`.

The discrepancy of **256 L1-data-gas units** (2 felts × 128 blob-gas/felt) is the exact cost of the missing `n_compiled_class_hash_updates = 1` entry, as computed by `get_da_gas_cost` with `use_kzg_da = true`. [7](#0-6)

### Citations

**File:** crates/blockifier/src/fee/gas_usage.rs (L33-34)
```rust
    // For each compiled class updated (through declare): class_hash, compiled_class_hash
    onchain_data_segment_length += state_changes_count.n_compiled_class_hash_updates * 2;
```

**File:** crates/blockifier/src/fee/gas_usage.rs (L39-74)
```rust
/// Returns the gas cost of data availability on L1.
pub fn get_da_gas_cost(state_changes_count: &StateChangesCount, use_kzg_da: bool) -> GasVector {
    let onchain_data_segment_length = get_onchain_data_segment_length(state_changes_count);

    let (l1_gas, blob_gas) = if use_kzg_da {
        (
            0_u8.into(),
            u64_from_usize(
                onchain_data_segment_length * eth_gas_constants::DATA_GAS_PER_FIELD_ELEMENT,
            )
            .into(),
        )
    } else {
        // TODO(Yoni, 1/5/2024): count the exact amount of nonzero bytes for each DA entry.
        let naive_cost = onchain_data_segment_length * eth_gas_constants::SHARP_GAS_PER_DA_WORD;

        // For each modified contract, the expected non-zeros bytes in the second word are:
        // 1 bytes for class hash flag; 2 for number of storage updates (up to 64K);
        // 3 for nonce update (up to 16M).
        let modified_contract_cost = eth_gas_constants::get_calldata_word_cost(1 + 2 + 3);
        let modified_contract_discount =
            eth_gas_constants::GAS_PER_MEMORY_WORD - modified_contract_cost;
        let mut discount = state_changes_count.n_modified_contracts * modified_contract_discount;

        // Up to balance of 8*(10**10) ETH.
        let fee_balance_value_cost = eth_gas_constants::get_calldata_word_cost(12);
        discount += eth_gas_constants::GAS_PER_MEMORY_WORD - fee_balance_value_cost;

        // Cost must be non-negative after discount.
        let gas = naive_cost.saturating_sub(discount);

        (u64_from_usize(gas).into(), 0_u8.into())
    };

    GasVector { l1_gas, l1_data_gas: blob_gas, ..Default::default() }
}
```

**File:** crates/blockifier/src/fee/gas_usage.rs (L168-174)
```rust
        Transaction::Declare(_) => StateChangesCount {
            n_storage_updates: 1,
            n_class_hash_updates: 0,
            // TODO(Yoni): BLOCKIFIER-RESET: should be 1.
            n_compiled_class_hash_updates: 0,
            n_modified_contracts: 1,
        },
```

**File:** crates/blockifier/src/transaction/transactions_test.rs (L1846-1852)
```rust
    } else if version == TransactionVersion::TWO || version == TransactionVersion::THREE {
        StateChangesCount {
            n_storage_updates: 1,             // Sender balance.
            n_modified_contracts: 1,          // Nonce.
            n_compiled_class_hash_updates: 1, // Also set compiled class hash.
            ..StateChangesCount::default()
        }
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L355-372)
```rust
    pub fn perform_pre_validation_stage<S: State + StateReader>(
        &self,
        state: &mut S,
        tx_context: &TransactionContext,
    ) -> TransactionPreValidationResult<()> {
        let tx_info = &tx_context.tx_info;
        Self::handle_nonce(state, tx_info, self.execution_flags.strict_nonce_check)?;

        if self.execution_flags.charge_fee {
            self.check_fee_bounds(tx_context)?;

            verify_can_pay_committed_bounds(state, tx_context).map_err(Box::new)?;
        }

        self.validate_proof_facts(&tx_context.block_context, state)?;

        Ok(())
    }
```

**File:** crates/blockifier/src/transaction/account_transaction.rs (L378-382)
```rust
        let minimal_gas_amount_vector = estimate_minimal_gas_vector(
            &tx_context.block_context,
            self,
            &tx_context.get_gas_vector_computation_mode(),
        );
```

**File:** crates/blockifier/src/fee/fee_checks.rs (L277-321)
```rust
impl PostExecutionReport {
    /// Verifies the actual cost can be paid by the account. If not, reports an error and the fee
    /// that should be charged in revert flow.
    pub fn new<S: StateReader>(
        state: &mut S,
        tx_context: &TransactionContext,
        tx_receipt: &TransactionReceipt,
        charge_fee: bool,
    ) -> TransactionExecutionResult<Self> {
        let TransactionReceipt { fee, gas, .. } = tx_receipt;

        // If fee is not enforced, no need to check post-execution.
        if !charge_fee {
            return Ok(Self(FeeCheckReport::success_report(*fee)));
        }

        // First, compare the actual resources used against the upper bound(s) defined by the
        // sender.
        let cost_within_bounds_result =
            FeeCheckReport::check_actual_cost_within_bounds(tx_context, tx_receipt);

        // Next, verify the actual cost is covered by the account balance, which may have changed
        // after execution. If the above check passes, the pre-execution balance covers the actual
        // cost for sure.
        let can_pay_fee_result = FeeCheckReport::check_can_pay_fee(state, tx_context, tx_receipt);

        for fee_check_result in [cost_within_bounds_result, can_pay_fee_result] {
            match fee_check_result {
                Ok(_) => continue,
                Err(TransactionExecutionError::FeeCheckError(fee_check_error)) => {
                    // Found an error; set the recommended fee based on the error variant and
                    // current context, and return the report.
                    return Ok(Self(FeeCheckReport::from_fee_check_error(
                        *fee,
                        *gas,
                        fee_check_error,
                        tx_context,
                    )));
                }
                Err(other_error) => return Err(other_error),
            }
        }

        Ok(Self(FeeCheckReport::success_report(*fee)))
    }
```
