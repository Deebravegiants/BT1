### Title
Meta Transaction Sender Account Deletion Between Relayer Validation and Receipt Execution Causes Relayer Gas Loss - (File: runtime/runtime/src/actions.rs)

### Summary

In NEAR's meta transaction (NEP-366) system, a malicious `DelegateAction` sender can sign a valid delegate action, hand it to a relayer, then delete their own account (or the signing access key) before the delegate action receipt executes on their shard. The relayer's gas is committed at transaction-to-receipt conversion time; when the receipt later fails with `DelegateActionAccessKeyError::AccessKeyNotFound`, the relayer's NEAR tokens are already burnt with no recourse against the sender.

### Finding Description

The meta transaction flow has a two-phase structure with a timing gap:

**Phase 1 – Relayer validation and gas commitment** (`runtime/runtime/src/lib.rs`, `process_transactions`):

When the relayer submits the outer transaction, `process_transactions` converts it to a receipt and charges the relayer's account for all gas costs. [1](#0-0)  The relayer's balance is debited at this point. The sender's account state is not re-verified here; only the relayer's signer account and access key are checked.

**Phase 2 – Delegate action receipt execution** (`runtime/runtime/src/actions.rs`, `apply_delegate_action`):

The receipt is forwarded to the sender's shard and `apply_delegate_action` is called. It validates the sender's access key via `validate_delegate_action_key`. [2](#0-1)  The comment inside `validate_delegate_action_key` explicitly states: `// 'sender_id' account existence must be checked by a caller` — but `apply_delegate_action` performs no explicit account existence check before calling it. [3](#0-2) 

If the sender deleted their account (or the specific signing key) between Phase 1 and Phase 2, `get_access_key` returns `None`, the action fails with `DelegateActionAccessKeyError::AccessKeyNotFound`, and the relayer's already-committed gas is burnt. The sender pays nothing and may even recover storage-staking tokens from the deletion.

The code comment in `apply_delegate_action` acknowledges the relayer bears all costs but only advises the relayer to "verify DelegateAction before submitting it" — which does not protect against the timing window: [4](#0-3) 

The design documentation explicitly acknowledges this attack surface: [5](#0-4) 

### Impact Explanation

The relayer loses NEAR tokens (gas) with no recourse. The corrupted protocol value is the **relayer's balance**: it is decremented at transaction processing time and cannot be recovered when the delegate action receipt fails due to sender account deletion. The sender's balance is unaffected (or even increased by recovering storage stake). This is a direct, measurable financial loss to an honest relayer, not merely a denial of service.

### Likelihood Explanation

The attack is straightforward for any unprivileged user:

1. Alice signs a `DelegateAction` with a valid nonce and sends it off-chain to a relayer.
2. Alice simultaneously submits a `DeleteAccount` (or `DeleteKey`) transaction to the network.
3. Both transactions land in the same chunk on Alice's shard.
4. In `process_transactions`, all transactions are converted to receipts first. Alice's `DeleteAccount` receipt and the relayer's delegate action receipt are both queued as local receipts.
5. In `process_receipts`, Alice's `DeleteAccount` receipt executes first (it was enqueued first if Alice's transaction preceded the relayer's in the chunk).
6. Alice's account is deleted; the delegate action receipt then fails with `AccessKeyNotFound`.
7. The relayer's gas is already burnt.

Alice controls the timing by submitting her `DeleteAccount` transaction at the same moment she hands the `DelegateAction` to the relayer. No validator or privileged access is required. The attack can be repeated at scale against any public relayer service.

### Recommendation

1. **Protocol-level**: When a delegate action receipt fails due to `DelegateActionAccessKeyError` or `AccountDoesNotExist` on the sender's shard, the runtime should attempt to charge the sender's account for the gas cost before falling back to burning it. If the sender's account no longer exists, the gas is unrecoverable, but this at least removes the financial incentive for the attack when the account still has balance.

2. **Relayer-level mitigation** (insufficient alone): Relayers should re-query the sender's account and access key state immediately before broadcasting the outer transaction, and use a short `max_block_height` in the `DelegateAction` to minimize the timing window.

3. **Protocol-level alternative**: Require the sender to attach a small NEAR deposit to the `DelegateAction` (held in escrow) that is forfeited to the relayer if the delegate action fails due to sender-side key/account absence.

### Proof of Concept

```
1. Alice creates account "alice.near" with full-access key K.
2. Alice signs DelegateAction {
       sender_id: "alice.near",
       receiver_id: "token.near",
       actions: [FunctionCall { method: "ft_transfer", gas: 300 TGas, ... }],
       nonce: current_nonce + 1,
       max_block_height: current_height + 10,
       public_key: K,
   } and sends it off-chain to an honest relayer.
3. Alice simultaneously broadcasts:
       SignedTransaction { signer: "alice.near", receiver: "alice.near",
           actions: [DeleteAccount { beneficiary: "alice.near" }] }
4. Both transactions are included in the same chunk on alice.near's shard.
5. process_transactions runs:
   - Alice's DeleteAccount tx → local receipt R1 (delete alice.near)
   - Relayer's tx → local receipt R2 (delegate action to alice.near)
   - Relayer's balance is debited for all gas.
6. process_receipts runs:
   - R1 executes: alice.near is deleted, storage stake returned to Alice.
   - R2 executes: apply_delegate_action → validate_delegate_action_key →
     get_access_key returns None → DelegateActionAccessKeyError::AccessKeyNotFound.
7. Relayer's gas is burnt. Alice paid nothing for the failed meta transaction
   and recovered her storage stake.
```

The root cause is at `runtime/runtime/src/actions.rs` lines 422–491 (`apply_delegate_action`) and `runtime/runtime/src/actions.rs` lines 530–556 (`validate_delegate_action_key`), with gas commitment occurring in `runtime/runtime/src/lib.rs` lines 1853–2100 (`process_transactions`). [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** runtime/runtime/src/lib.rs (L1853-1858)
```rust
    fn process_transactions(
        &self,
        processing_state: &mut ApplyProcessingReceiptState,
        signed_txs: SignedValidPeriodTransactions,
        receipt_sink: &mut ReceiptSink,
    ) -> Result<(), RuntimeError> {
```

**File:** runtime/runtime/src/lib.rs (L1993-2030)
```rust
            let mut account = accounts.get_mut(signer_id);
            let account = match account.as_deref_mut() {
                Some(Ok(Some(a))) => a,
                Some(Ok(None)) => {
                    metrics::TRANSACTION_PROCESSED_FAILED_TOTAL.inc();
                    tracing::debug!(%tx_hash, "transaction signed by unknown account");
                    let outcome = ExecutionOutcomeWithId::failed(
                        tx,
                        InvalidTxError::InvalidSignerId { signer_id: signer_id.to_string() },
                    );
                    processing_state.outcomes.push(outcome);
                    continue;
                }
                Some(Err(e)) => return Err(e.clone().into()),
                None => unreachable!("accounts should've been prefetched"),
            };
            let mut access_key = access_keys.get_mut(&(signer_id, pubkey));
            let access_key = match access_key.as_deref_mut() {
                Some(Ok(Some(ak))) => ak,
                Some(Ok(None)) => {
                    metrics::TRANSACTION_PROCESSED_FAILED_TOTAL.inc();
                    tracing::debug!(%tx_hash, "transaction signed by unknown signing key");
                    let outcome = ExecutionOutcomeWithId::failed(
                        tx,
                        InvalidTxError::InvalidAccessKeyError(
                            InvalidAccessKeyError::AccessKeyNotFound {
                                account_id: signer_id.clone(),
                                public_key: Box::new(pubkey.clone()),
                            },
                        ),
                    );

                    processing_state.outcomes.push(outcome);
                    continue;
                }
                Some(Err(e)) => return Err(e.clone().into()),
                None => unreachable!("access keys should've been prefetched"),
            };
```

**File:** runtime/runtime/src/actions.rs (L422-491)
```rust
pub(crate) fn apply_delegate_action(
    state_update: &mut TrieUpdate,
    apply_state: &ApplyState,
    action_receipt: &VersionedActionReceipt,
    sender_id: &AccountId,
    signed_delegate_action: VersionedSignedDelegateActionRef<'_>,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    if !signed_delegate_action.verify() {
        result.result = Err(ActionErrorKind::DelegateActionInvalidSignature.into());
        return Ok(());
    }
    let delegate_action = signed_delegate_action.delegate_action();
    if apply_state.block_height > delegate_action.max_block_height() {
        result.result = Err(ActionErrorKind::DelegateActionExpired.into());
        return Ok(());
    }
    if delegate_action.sender_id().as_str() != sender_id.as_str() {
        result.result = Err(ActionErrorKind::DelegateActionSenderDoesNotMatchTxReceiver {
            sender_id: delegate_action.sender_id().clone(),
            receiver_id: sender_id.clone(),
        }
        .into());
        return Ok(());
    }

    validate_delegate_action_key(state_update, apply_state, delegate_action, result)?;
    if result.result.is_err() {
        // Validation failed. Need to return Ok() because this is not a runtime error.
        // "result.result" will be return to the User as the action execution result.
        return Ok(());
    }

    // Generate a new receipt from DelegateAction.
    let new_receipt = Receipt::V0(ReceiptV0 {
        predecessor_id: sender_id.clone(),
        receiver_id: delegate_action.receiver_id().clone(),
        receipt_id: CryptoHash::default(),

        receipt: ReceiptEnum::Action(ActionReceipt {
            signer_id: action_receipt.signer_id().clone(),
            signer_public_key: action_receipt.signer_public_key().clone(),
            gas_price: action_receipt.gas_price(),
            output_data_receivers: vec![],
            input_data_ids: vec![],
            actions: delegate_action.get_actions(),
        }),
    });

    // Note, Relayer prepaid all fees and all things required by actions: attached deposits and attached gas.
    // If something goes wrong, deposit is refunded to the predecessor, this is sender_id/Sender in DelegateAction.
    // Gas is refunded to the signer, this is Relayer.
    // Some contracts refund the deposit. Usually they refund the deposit to the predecessor and this is sender_id/Sender from DelegateAction.
    // Therefore Relayer should verify DelegateAction before submitting it because it spends the attached deposit.

    let prepaid_send_fees = total_prepaid_send_fees(&apply_state.config, action_receipt.actions())?;
    let required_cost = receipt_required_cost(apply_state, &new_receipt)?;
    // This gas will be burnt by the receiver of the created receipt.
    // Compute costs of that are not relevant at this point, the "used" gas is
    // only reserved for execution later, potentially on a different shard.
    result.gas_used = result.gas_used.checked_add_result(required_cost.gas)?;
    // This gas was prepaid on Relayer shard. Need to burn it because the receipt is going to be sent.
    // gas_used is incremented because otherwise the gas will be refunded. Refund function checks only gas_used.
    result.gas_used = result.gas_used.checked_add_result(prepaid_send_fees.gas)?;
    result.gas_burnt = result.gas_burnt.checked_add_result(prepaid_send_fees.gas)?;
    result.compute_usage = safe_add_compute(result.compute_usage, prepaid_send_fees.compute)?;
    result.new_receipts.push(new_receipt);

    Ok(())
}
```

**File:** runtime/runtime/src/actions.rs (L530-556)
```rust
/// Validate access key which was used for signing DelegateAction:
///
/// - Checks whether the access key is present fo given public_key and sender_id.
/// - Validates nonce and updates it if it's ok.
/// - Validates access key permissions.
fn validate_delegate_action_key(
    state_update: &mut TrieUpdate,
    apply_state: &ApplyState,
    delegate_action: VersionedDelegateActionRef<'_>,
    result: &mut ActionResult,
) -> Result<(), RuntimeError> {
    let sender_id = delegate_action.sender_id();
    let public_key = delegate_action.public_key();
    // 'sender_id' account existence must be checked by a caller
    let mut access_key = match get_access_key(state_update, sender_id, public_key)? {
        Some(access_key) => access_key,
        None => {
            result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                InvalidAccessKeyError::AccessKeyNotFound {
                    account_id: sender_id.clone(),
                    public_key: public_key.clone().into(),
                },
            )
            .into());
            return Ok(());
        }
    };
```

**File:** docs/architecture/how/meta-tx.md (L145-150)
```markdown
Once again, some trust is required. If Alice wanted to abuse the relayer's
helpful service, she could ask the relayer to initialize her account.
Afterwards, she does not sign a meta transaction, instead she deletes her
account and cashes in the small token balance reserved for storage. If this
attack is repeated, a significant amount of tokens could be stolen from the
relayer.
```
