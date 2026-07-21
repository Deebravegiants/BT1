### Title
Concurrent fee-transfer completion overwrites execute-phase sequencer balance writes, producing wrong committed storage value — (`crates/blockifier/src/concurrency/fee_utils.rs`)

---

### Summary

In concurrent block execution, when a transaction's **execute phase** transfers tokens to the sequencer address AND the transaction also pays a fee, the commit-time `add_fee_to_sequencer_balance` call reads the sequencer balance from the **pre-execute-phase committed state** and inserts `committed_balance + fee` into `execution_output.state_diff`, silently overwriting the execute-phase write of `committed_balance + transfer_amount`. The `transfer_amount` tokens are erased from the committed state.

---

### Finding Description

The concurrent fee-transfer design has two stages:

**Stage 1 – execution time** (`concurrency_execute_fee_transfer`):
The fee transfer is executed inside a sub-transactional state where the sequencer balance is forced to `ZERO`. After the ERC20 `transfer` call completes, the sequencer balance writes are **removed** from the sub-state before it is committed back to the outer state. This leaves the outer state's cache with only the execute-phase writes. [1](#0-0) 

**Stage 2 – commit time** (`complete_fee_transfer_flow` → `add_fee_to_sequencer_balance`):
`tx_versioned_state` is pinned at `tx_index` and sees only previously committed transactions — it does **not** see the current transaction's own execute-phase writes. `add_fee_to_sequencer_balance` reads `committed_balance` from this view, computes `committed_balance + fee`, and calls `state_diff.storage.insert(...)`. [2](#0-1) [3](#0-2) 

**The collision**: If the execute phase wrote `committed_balance + transfer_amount` to `execution_output.state_diff` for the sequencer balance key (e.g., the user called `ERC20.transfer(sequencer_address, transfer_amount)`), the `HashMap::insert` at commit time **overwrites** that entry with `committed_balance + fee`. The `transfer_amount` is silently dropped from the state diff and from the versioned state slot. [4](#0-3) 

The `fill_sequencer_balance_reads` assertion (`storage_read_values[index] == ZERO`) does not catch this because the fee transfer call info was correctly produced with a forced-zero balance — the assertion passes while the state diff is already corrupted. [5](#0-4) 

---

### Impact Explanation

The committed block's storage value for the sequencer's fee-token balance is `committed_balance + fee` instead of `committed_balance + transfer_amount + fee`. The `transfer_amount` tokens are burned: deducted from the sender's balance (correctly) but never credited to the sequencer in the final state. This produces a wrong state root and a wrong storage value for every block that contains such a transaction. It falls squarely under:

> *Critical. Wrong state … storage value … from blockifier/syscall/execution logic for accepted input.*
> *Incorrect … balance … with economic impact.*

---

### Likelihood Explanation

Any unprivileged user can craft an invoke transaction whose calldata calls `ERC20.transfer(sequencer_address, amount)` in the execute phase. No special role, no privileged access, and no coordination with other parties is required. The sequencer runs in concurrent mode by default (`n_concurrent_txs > 1`). The bug fires on every such transaction.

---

### Recommendation

In `add_fee_to_sequencer_balance`, instead of reading the sequencer balance exclusively from the committed versioned state, first check whether `state_diff.storage` already contains an entry for `(fee_token_address, sequencer_balance_key_low/high)`. If it does, use that value as the base for the addition rather than the committed-state value. This ensures that execute-phase writes to the sequencer balance are preserved and the fee is added on top of them, not in place of them.

```rust
// Pseudocode fix in add_fee_to_sequencer_balance:
let base_low = state_diff.storage
    .get(&(fee_token_address, sequencer_balance_key_low))
    .map(|f| f.to_u128().unwrap())
    .unwrap_or(sequencer_balance_low_as_u128);  // fall back to committed balance

let (new_value_low, overflow_low) = base_low.overflowing_add(actual_fee.0);
// ... same for high ...
```

---

### Proof of Concept

1. Sequencer runs with `n_concurrent_txs ≥ 2`. Sequencer address is `S`. Committed sequencer balance is `B`.
2. User submits an invoke transaction `T` with:
   - Execute calldata: `ERC20.transfer(S, 1000)`
   - Actual fee: `100`
3. `T` executes concurrently. Execute phase writes `(fee_token, seq_key_low) → B + 1000` into `execution_output.state_diff`.
4. `concurrency_execute_fee_transfer` runs: forces seq balance to `0`, executes fee transfer (call info records `0` as seq balance), removes seq balance writes from sub-state. Outer state_diff retains `B + 1000`.
5. At commit time, `complete_fee_transfer_flow` reads `B` from `tx_versioned_state` (pre-execute view). Calls `add_fee_to_sequencer_balance(fee=100, seq_balance=(B,0))`.
6. `add_fee_to_sequencer_balance` inserts `(fee_token, seq_key_low) → B + 100` into `execution_output.state_diff`, **overwriting** `B + 1000`.
7. Committed state: sequencer balance = `B + 100`. The 1000 tokens transferred by the user are burned. State root is wrong.

### Citations

**File:** crates/blockifier/src/transaction/account_transaction.rs (L607-621)
```rust
        let mut transfer_state = TransactionalState::create_transactional(state);

        // Set the initial sequencer balance to avoid tarnishing the read-set of the transaction.
        let cache = transfer_state.cache.get_mut();
        for key in [sequencer_balance_key_low, sequencer_balance_key_high] {
            cache.set_storage_initial_value(fee_address, key, Felt::ZERO);
        }

        let fee_transfer_call_info =
            Self::execute_fee_transfer(&mut transfer_state, tx_context, actual_fee);
        // Commit without updating the sequencer balance.
        let storage_writes = &mut transfer_state.cache.get_mut().writes.storage;
        storage_writes.remove(&(fee_address, sequencer_balance_key_low));
        storage_writes.remove(&(fee_address, sequencer_balance_key_high));
        transfer_state.commit();
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L38-62)
```rust
    if let Some(fee_transfer_call_info) = tx_execution_info.fee_transfer_call_info.as_mut() {
        let sequencer_balance = state
        .get_fee_token_balance(
            tx_context.block_context.block_info.sequencer_address,
            tx_context.fee_token_address()
        )
        // TODO(barak, 01/07/2024): Consider propagating the error.
        .unwrap_or_else(|error| {
            panic!(
                "Access to storage failed. Probably due to a bug in Papyrus. {error:?}: {error}"
            )
        });

        // Fix the transfer call info.
        fill_sequencer_balance_reads(fee_transfer_call_info, sequencer_balance);
        // Update the balance.
        add_fee_to_sequencer_balance(
            tx_context.fee_token_address(),
            state,
            tx_execution_info.receipt.fee,
            &tx_context.block_context,
            sequencer_balance,
            tx_context.tx_info.sender_address(),
            state_diff,
        );
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L96-102)
```rust
    let (low_index, high_index) = STORAGE_READ_SEQUENCER_BALANCE_INDICES;
    for index in [low_index, high_index] {
        assert_eq!(storage_read_values[index], Felt::ZERO, "Sequencer balance should be zero");
    }
    let (low, high) = sequencer_balance;
    storage_read_values[low_index] = low;
    storage_read_values[high_index] = high;
```

**File:** crates/blockifier/src/concurrency/fee_utils.rs (L130-157)
```rust
    let (sequencer_balance_key_low, sequencer_balance_key_high) =
        get_sequencer_balance_keys(block_context);
    let writes = StateMaps {
        storage: HashMap::from([
            ((fee_token_address, sequencer_balance_key_low), Felt::from(new_value_low)),
            ((fee_token_address, sequencer_balance_key_high), Felt::from(new_value_high)),
        ]),
        ..StateMaps::default()
    };

    // Modify state_diff to accurately reflect the post tx-execution state, after fee transfer to
    // the sequencer. We assume that a non-sequencer sender cannot reduce the sequencer's
    // balance—only increases are possible.

    if sequencer_balance_high_as_u128 != new_value_high {
        // Update the high balance only if it has changed.
        state_diff
            .storage
            .insert((fee_token_address, sequencer_balance_key_high), Felt::from(new_value_high));
    }

    if sequencer_balance_low_as_u128 != new_value_low {
        // Update the low balance only if it has changed.
        state_diff
            .storage
            .insert((fee_token_address, sequencer_balance_key_low), Felt::from(new_value_low));
    }
    state.apply_writes(&writes, &ContractClassMapping::default());
```
