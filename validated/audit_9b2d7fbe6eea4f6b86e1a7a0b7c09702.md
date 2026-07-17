### Title
Deposit Refund Sent to Wrong Account in Meta-Transaction (DelegateAction) Failure - (File: `runtime/runtime/src/actions.rs`)

### Summary
When a meta-transaction (`DelegateAction`) inner receipt fails on the receiver's shard, the attached deposit is refunded to the inner sender (Alice), not to the relayer who actually paid the deposit. An unprivileged user can exploit this by crafting a `DelegateAction` with a large attached deposit designed to fail, causing the relayer to permanently lose the deposit while the user gains it.

### Finding Description
In `apply_delegate_action` (`runtime/runtime/src/actions.rs`), when a `DelegateAction` is processed on Alice's shard, a new inner receipt is constructed with `predecessor_id` set to `sender_id` (Alice, the inner signer), while `signer_id` is set to `action_receipt.signer_id()` (the relayer): [1](#0-0) 

The relayer's account is debited for the full deposit when the outer transaction is converted to a receipt. However, when the inner receipt fails on the receiver's shard, `refund_unspent_gas_and_deposits` in `runtime/runtime/src/lib.rs` issues the deposit refund to `receipt.balance_refund_receiver()`: [2](#0-1) 

`balance_refund_receiver()` resolves to `receipt.predecessor_id()` when no `refund_to` override is set: [3](#0-2) 

Since the inner receipt's `predecessor_id` is Alice (not the relayer), the deposit refund is sent to Alice. The relayer paid the deposit but Alice receives it back on failure.

This is explicitly acknowledged in the protocol documentation as a known financial risk: [4](#0-3) 

The comment in `apply_delegate_action` itself notes the asymmetry: [5](#0-4) 

### Impact Explanation
The corrupted protocol value is the **balance** of the relayer account. The relayer's balance is permanently reduced by the deposit amount, while Alice's balance is increased by the same amount, with no legitimate transfer having occurred. This is a direct, unprivileged theft of the relayer's deposited tokens. The magnitude is bounded only by the deposit amount Alice includes in the `DelegateAction`.

### Likelihood Explanation
Any user (Alice) who can submit a `DelegateAction` through the normal public RPC path can trigger this. The attack requires:
1. Alice crafts a `DelegateAction` with a large `deposit` attached to a function call targeting a contract that will fail (e.g., a non-existent method, or a contract that panics).
2. A relayer submits it, paying the deposit upfront.
3. The inner receipt fails on the receiver's shard.
4. The deposit is refunded to Alice.

No special privileges are required. The attack is repeatable and the financial incentive for Alice is explicit: she receives the relayer's deposit for free. The protocol documentation itself identifies this as a financial incentive for abuse.

### Recommendation
When constructing the inner receipt in `apply_delegate_action`, set `predecessor_id` to the relayer's account ID (i.e., `action_receipt.signer_id()`) rather than `sender_id`, so that deposit refunds on failure return to the party that paid them. Alternatively, use the `refund_to` field (available in `ActionReceiptV2`) to explicitly redirect deposit refunds to the relayer's account, preserving `predecessor_id` as Alice for contract-level `predecessor_account_id()` semantics.

### Proof of Concept
1. Relayer submits a transaction wrapping Alice's `DelegateAction`:
   - Inner action: `FunctionCall` to `bob.near` calling `nonexistent_method` with `deposit = 10 NEAR`
   - Alice signs the `DelegateAction`; relayer signs the outer transaction
2. Outer transaction converts to a receipt; relayer's account is debited `10 NEAR` deposit + gas
3. On Alice's shard, `apply_delegate_action` creates an inner receipt with `predecessor_id = alice.near`, `signer_id = relayer.near`
4. Inner receipt executes on Bob's shard; `nonexistent_method` fails
5. `refund_unspent_gas_and_deposits` issues `Receipt::new_balance_refund(&alice.near, 10 NEAR)`
6. Alice receives `10 NEAR`; relayer's net loss = `10 NEAR` deposit (gas refund correctly goes to relayer via `signer_id`)

The existing test `test_gas_key_refund` in `test-loop-tests/src/tests/gas_keys.rs` demonstrates the split refund behavior (gas to signer, deposit to predecessor), confirming the mechanism is live: [6](#0-5)

### Citations

**File:** runtime/runtime/src/actions.rs (L455-469)
```rust
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
```

**File:** runtime/runtime/src/actions.rs (L471-475)
```rust
    // Note, Relayer prepaid all fees and all things required by actions: attached deposits and attached gas.
    // If something goes wrong, deposit is refunded to the predecessor, this is sender_id/Sender in DelegateAction.
    // Gas is refunded to the signer, this is Relayer.
    // Some contracts refund the deposit. Usually they refund the deposit to the predecessor and this is sender_id/Sender from DelegateAction.
    // Therefore Relayer should verify DelegateAction before submitting it because it spends the attached deposit.
```

**File:** runtime/runtime/src/lib.rs (L1269-1273)
```rust
        if deposit_refund > Balance::ZERO {
            result.new_receipts.push(Receipt::new_balance_refund(
                receipt.balance_refund_receiver(),
                deposit_refund,
            ));
```

**File:** core/primitives/src/receipt.rs (L428-430)
```rust
    pub fn balance_refund_receiver(&self) -> &AccountId {
        self.refund_to().as_ref().unwrap_or_else(|| self.predecessor_id())
    }
```

**File:** docs/architecture/how/meta-tx.md (L225-242)
```markdown
## Balance refunds in meta transactions

Unlike gas refunds, the protocol sends balance refunds to the predecessor
(a.k.a. sender) of the receipt. This makes sense, as we deposit the attached
balance to the receiver, who has to explicitly reattach a new balance to new
receipts they might spawn.

In the world of meta transactions, this assumption is also challenged. If an
inner action requires an attached balance (for example a transfer action) then
this balance is taken from the relayer.

The relayer can see what the cost will be before submitting the meta transaction
and agrees to pay for it, so nothing wrong so far. But what if the transaction
fails execution on Bob's shard? At this point, the predecessor is `Alice` and
therefore she receives the token balance refunded, not the relayer. This is
something relayer implementations must be aware of since there is a financial
incentive for Alice to submit meta transactions that have high balances attached
but will fail on Bob's shard.
```

**File:** test-loop-tests/src/tests/gas_keys.rs (L385-393)
```rust
    // Verify gas key balance: should be initial minus tokens_burnt (gas refund went back to gas key).
    let (_, gas_key_balance_after) =
        query_gas_key_and_balance(&env.rpc_node(), sender, &gas_key_signer.public_key());
    assert_eq!(gas_key_balance_after, gas_key_balance_before.checked_sub(tokens_burnt).unwrap());

    // Verify sender account balance is unchanged: deposit was deducted when the tx was
    // converted to a receipt, then refunded when the function call failed.
    let sender_balance_after = env.rpc_node().view_account_query(sender).unwrap().amount;
    assert_eq!(sender_balance_after, sender_balance_before);
```
