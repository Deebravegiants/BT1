### Title
Duplicate `input_data_ids` in ActionReceipt Inflate `PendingDataCount`, Permanently Freezing Postponed Receipts - (File: `runtime/runtime/src/lib.rs`)

### Summary

`process_action_receipt` counts each entry in `input_data_ids` independently when computing `pending_data_count`, without deduplicating. If a receipt carries the same `data_id` twice, the counter is set to 2 while only one unique `DataReceipt` will ever arrive. The `PostponedReceiptId` mapping is overwritten with the same value on the second iteration, so only one decrement ever fires. The postponed receipt is permanently stuck in trie state and never executes.

### Finding Description

In `process_action_receipt` (`runtime/runtime/src/lib.rs`), the loop over `action_receipt.input_data_ids()` increments `pending_data_count` for every entry that is not yet in state, and writes `TrieKey::PostponedReceiptId { data_id }` → `receipt_id` for each such entry: [1](#0-0) 

If `input_data_ids` is `[data_id_A, data_id_A]`:
- Iteration 1: `data_id_A` absent → `pending_data_count = 1`, `PostponedReceiptId[data_id_A] = receipt_id`
- Iteration 2: `data_id_A` still absent (same trie state within the same call) → `pending_data_count = 2`, `PostponedReceiptId[data_id_A] = receipt_id` (overwritten with identical value)

`PendingDataCount` is then stored as `2`: [2](#0-1) 

When the single `DataReceipt` for `data_id_A` arrives, `process_receipt` decrements `PendingDataCount` from 2 to 1 and removes `PostponedReceiptId[data_id_A]`: [3](#0-2) 

Because the count is now 1 (not 0), the postponed receipt is not executed. No second `DataReceipt` for `data_id_A` will ever arrive (the `PostponedReceiptId` mapping was already removed), so the count can never reach 0. The postponed receipt and its `PendingDataCount` entry remain in the trie permanently.

The receipt validation function `validate_action_receipt` only enforces a count limit on `input_data_ids`; it performs no uniqueness check: [4](#0-3) 

The `ActionReceiptMetadata` struct stores `input_data_ids` as a plain `Vec<CryptoHash>` with no deduplication: [5](#0-4) 

### Impact Explanation

The corrupted protocol value is `TrieKey::PendingDataCount { receiver_id, receipt_id }` in the shard's Merkle-Patricia trie. It is permanently set to a non-zero value for a receipt that will never execute. Consequences:

1. **Permanent state corruption**: The postponed receipt and its `PendingDataCount` entry are orphaned in the state root forever, diverging from the invariant that every postponed receipt eventually executes.
2. **Permanent loss of attached deposit**: Any `NEAR` tokens attached to the stuck receipt are unrecoverable.
3. **Gas loss**: Gas prepaid for the receipt is consumed with no execution outcome.

### Likelihood Explanation

A malicious smart contract deployed via a standard public RPC transaction can call `promise_and` (or equivalent host functions) passing the same promise index twice. The NEAR VM logic passes the resulting `input_data_ids` directly into `create_action_receipt` as a `Vec<CryptoHash>` without deduplication: [6](#0-5) 

The receipt format explicitly allows duplicate entries (the existing test at line 1900 of `verifier.rs` constructs `input_data_ids: vec![CryptoHash::default(), CryptoHash::default()]` without rejection on uniqueness grounds): [7](#0-6) 

Any unprivileged account can deploy a contract and trigger this path through a signed transaction submitted to the public RPC.

### Recommendation

In `process_action_receipt`, deduplicate `input_data_ids` before iterating, or track already-counted `data_id`s in a local `HashSet` and skip duplicates:

```rust
let mut seen = HashSet::new();
for data_id in action_receipt.input_data_ids() {
    if !seen.insert(*data_id) {
        continue; // skip duplicate
    }
    if !has_received_data(state_update, account_id, *data_id)? {
        pending_data_count += 1;
        set(state_update, TrieKey::PostponedReceiptId { ... }, receipt.receipt_id());
    }
}
```

Alternatively, add a uniqueness check to `validate_action_receipt` that rejects receipts with duplicate `input_data_ids` as a `ReceiptValidationError`.

### Proof of Concept

1. Attacker deploys a contract on shard S that, when called, uses `promise_and` with the same sub-promise index twice, producing an `ActionReceipt` with `input_data_ids = [data_id_A, data_id_A]` targeting account `victim.near`.
2. The chunk producer includes the transaction; the runtime calls `process_action_receipt`. `pending_data_count` is set to 2 and stored under `TrieKey::PendingDataCount { receiver_id: "victim.near", receipt_id }`.
3. The single `DataReceipt` for `data_id_A` arrives in a subsequent chunk. `process_receipt` decrements `PendingDataCount` to 1 and removes `PostponedReceiptId[data_id_A]`.
4. No further `DataReceipt` for `data_id_A` will ever arrive. `PendingDataCount` remains 1 in the trie permanently.
5. The postponed receipt is never executed. Any deposit attached to it is permanently locked. The state root of shard S now contains an orphaned `PostponedReceipt` and `PendingDataCount` entry that violates the protocol invariant that all postponed receipts eventually execute. [1](#0-0) [8](#0-7)

### Citations

**File:** runtime/runtime/src/lib.rs (L1328-1393)
```rust
                    state_update.remove(TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: data_receipt.data_id,
                    });
                    // Checking how many input data items is pending for the receipt.
                    let pending_data_count: u32 = get(
                        state_update,
                        &TrieKey::PendingDataCount { receiver_id: account_id.clone(), receipt_id },
                    )?
                    .ok_or_else(|| {
                        StorageError::StorageInconsistentState(
                            "pending data count should be in the state".to_string(),
                        )
                    })?;
                    if pending_data_count == 1 {
                        // It was the last input data pending for this receipt. We'll cleanup
                        // some receipt related fields from the state and execute the receipt.

                        // Removing pending data count from the state.
                        state_update.remove(TrieKey::PendingDataCount {
                            receiver_id: account_id.clone(),
                            receipt_id,
                        });
                        // Fetching the receipt itself.
                        let ready_receipt =
                            get_postponed_receipt(state_update, account_id, receipt_id)?
                                .ok_or_else(|| {
                                    StorageError::StorageInconsistentState(
                                        "pending receipt should be in the state".to_string(),
                                    )
                                })?;
                        // Removing the receipt from the state.
                        remove_postponed_receipt(state_update, account_id, receipt_id);
                        // Executing the receipt. It will read all the input data and clean it up
                        // from the state.
                        return self
                            .apply_action_receipt(
                                state_update,
                                apply_state,
                                pipeline_manager,
                                &ready_receipt,
                                receipt_sink,
                                instant_receipts,
                                validator_proposals,
                                stats,
                                epoch_info_provider,
                                receipt_to_tx,
                            )
                            .map(Some);
                    } else {
                        // There is still some pending data for the receipt, so we update the
                        // pending data count in the state.
                        set(
                            state_update,
                            TrieKey::PendingDataCount {
                                receiver_id: account_id.clone(),
                                receipt_id,
                            },
                            &(pending_data_count.checked_sub(1).ok_or_else(|| {
                                StorageError::StorageInconsistentState(
                                    "pending data count is 0, but there is a new DataReceipt"
                                        .to_string(),
                                )
                            })?),
                        );
                    }
```

**File:** runtime/runtime/src/lib.rs (L1529-1544)
```rust
        let mut pending_data_count: u32 = 0;
        for data_id in action_receipt.input_data_ids() {
            if !has_received_data(state_update, account_id, *data_id)? {
                pending_data_count += 1;
                // The data for a given data_id is not available, so we save a link to this
                // receipt_id for the pending data_id into the state.
                set(
                    state_update,
                    TrieKey::PostponedReceiptId {
                        receiver_id: account_id.clone(),
                        data_id: *data_id,
                    },
                    receipt.receipt_id(),
                )
            }
        }
```

**File:** runtime/runtime/src/lib.rs (L1566-1576)
```rust
            set(
                state_update,
                TrieKey::PendingDataCount {
                    receiver_id: account_id.clone(),
                    receipt_id: *receipt.receipt_id(),
                },
                &pending_data_count,
            );
            // Save the receipt itself into the state.
            set_postponed_receipt(state_update, receipt);
        }
```

**File:** runtime/runtime/src/verifier.rs (L588-616)
```rust
fn validate_action_receipt(
    limit_config: &LimitConfig,
    receipt: VersionedActionReceipt,
    receiver: &AccountId,
    current_protocol_version: ProtocolVersion,
    mode: ValidateReceiptMode,
) -> Result<(), ReceiptValidationError> {
    if receipt.input_data_ids().len() as u64 > limit_config.max_number_input_data_dependencies {
        return Err(ReceiptValidationError::NumberInputDataDependenciesExceeded {
            number_of_input_data_dependencies: receipt.input_data_ids().len() as u64,
            limit: limit_config.max_number_input_data_dependencies,
        });
    }

    if let Some(account_id) = receipt.refund_to() {
        AccountId::validate(account_id.as_ref()).map_err(|_| {
            ReceiptValidationError::InvalidRefundTo { account_id: account_id.to_string() }
        })?;
    }

    validate_actions_with_mode(
        limit_config,
        receipt.actions(),
        receiver,
        current_protocol_version,
        mode,
    )
    .map_err(ReceiptValidationError::ActionsValidation)
}
```

**File:** runtime/runtime/src/verifier.rs (L1887-1913)
```rust
    #[test]
    fn test_validate_action_receipt_too_many_input_deps() {
        let mut limit_config = test_limit_config();
        limit_config.max_number_input_data_dependencies = 1;
        let receiver = "alice.near".parse().unwrap();
        assert_eq!(
            validate_action_receipt(
                &limit_config,
                ActionReceipt {
                    signer_id: alice_account(),
                    signer_public_key: PublicKey::empty(KeyType::ED25519),
                    gas_price: Balance::from_yoctonear(100),
                    output_data_receivers: vec![],
                    input_data_ids: vec![CryptoHash::default(), CryptoHash::default()],
                    actions: vec![]
                }
                .into(),
                &receiver,
                PROTOCOL_VERSION,
                ValidateReceiptMode::NewReceipt,
            )
            .expect_err("expected an error"),
            ReceiptValidationError::NumberInputDataDependenciesExceeded {
                number_of_input_data_dependencies: 2,
                limit: 1
            }
        );
```

**File:** runtime/runtime/src/receipt_manager.rs (L29-47)
```rust
#[derive(Debug, Clone, PartialEq)]
pub struct ActionReceiptMetadata {
    /// Receipt destination
    pub receiver_id: AccountId,
    /// The account id to send balance refunds generated from this receipt.
    pub refund_to: Option<AccountId>,
    /// If present, where to route the output data
    pub output_data_receivers: Vec<DataReceiver>,
    /// A list of the input data dependencies for this Receipt to process.
    /// If all `input_data_ids` for this receipt are delivered to the account
    /// that means we have all the `ReceivedData` input which will be than converted to a
    /// `PromiseResult::Successful(value)` or `PromiseResult::Failed`
    /// depending on `ReceivedData` is `Some(_)` or `None`
    pub input_data_ids: Vec<CryptoHash>,
    /// A list of actions to process when all input_data_ids are filled
    pub actions: Vec<Action>,
    /// Indicates whether the receipt should have type Action or PromiseYield
    pub is_promise_yield: bool,
}
```

**File:** runtime/runtime/src/receipt_manager.rs (L111-136)
```rust
    pub(super) fn create_action_receipt(
        &mut self,
        input_data_ids: Vec<CryptoHash>,
        receipt_indices: Vec<ReceiptIndex>,
        receiver_id: AccountId,
    ) -> Result<ReceiptIndex, VMLogicError> {
        assert_eq!(input_data_ids.len(), receipt_indices.len());
        for (data_id, receipt_index) in input_data_ids.iter().zip(receipt_indices.into_iter()) {
            self.action_receipts
                .get_mut(receipt_index as usize)
                .ok_or(HostError::InvalidReceiptIndex { receipt_index })?
                .output_data_receivers
                .push(DataReceiver { data_id: *data_id, receiver_id: receiver_id.clone() });
        }

        let new_receipt = ActionReceiptMetadata {
            receiver_id,
            refund_to: None,
            output_data_receivers: vec![],
            input_data_ids,
            actions: vec![],
            is_promise_yield: false,
        };
        let new_receipt_index = self.action_receipts.len() as ReceiptIndex;
        self.action_receipts.push(new_receipt);
        Ok(new_receipt_index)
```
