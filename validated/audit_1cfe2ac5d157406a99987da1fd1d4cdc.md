### Title
Relayer's `signer_account_id` Exposed to Untrusted Contract Code in Meta-Transactions — (`runtime/runtime/src/actions.rs`)

### Summary
In NEAR's meta-transaction (NEP-366) implementation, `apply_delegate_action` propagates the relayer's account ID as the `signer_id` of the inner action receipt. Any contract invoked by the inner actions can read this via the `signer_account_id()` host function. A malicious user (Alice) can craft a `DelegateAction` targeting a contract that uses `signer_account_id()` for authorization, causing the contract to act on behalf of the relayer and drain the relayer's balance held in that contract.

### Finding Description
When `apply_delegate_action` processes a `SignedDelegateAction`, it constructs the forwarded inner receipt as follows:

```rust
receipt: ReceiptEnum::Action(ActionReceipt {
    signer_id: action_receipt.signer_id().clone(),       // ← relayer's account ID
    signer_public_key: action_receipt.signer_public_key().clone(), // ← relayer's key
    ...
    actions: delegate_action.get_actions(),
}),
``` [1](#0-0) 

This `signer_id` (the relayer) is then placed directly into the `VMContext` that is handed to the WASM contract:

```rust
let context = VMContext {
    signer_account_id: action_receipt.signer_id().clone(),  // relayer
    predecessor_account_id: predecessor_id.clone(),          // Alice (sender_id)
    ...
};
``` [2](#0-1) 

The contract can then call the `signer_account_id()` host function to retrieve the relayer's account ID: [3](#0-2) 

This is the NEAR equivalent of Solidity's `tx.origin`: `predecessor_account_id` is the immediate caller (Alice), while `signer_account_id` is the original transaction signer (the relayer). Any contract that uses `signer_account_id()` for authorization — for example, a staking contract, lending protocol, or any application that tracks deposits by original signer — will see the relayer's account ID and may act on it.

The NEAR documentation explicitly acknowledges that the relayer is the signer of the inner receipt:

> "All actions inside `delegate_action.actions` are submitted with the `delegate_action.sender_id` as the predecessor, `delegate_action.receiver_id` as the receiver, and the relayer (predecessor of `DelegateAction`) as the signer." [4](#0-3) 

However, the security implication — that user-controlled contract code can read and act on the relayer's identity — is not documented as a risk. The documentation only warns about the balance refund misdirection: [5](#0-4) 

### Impact Explanation
An unprivileged user (Alice) can craft a `DelegateAction` whose inner `FunctionCallAction` targets any contract that uses `signer_account_id()` for authorization. When the relayer submits this meta-transaction, the contract sees the relayer's account ID as the signer. If the relayer holds a balance in that contract (e.g., deposited via a third party, or the relayer's own account is registered in a fungible token or staking contract), the contract can execute a withdrawal or transfer on behalf of the relayer without the relayer's consent.

The corrupted protocol value is: **the relayer's token balance in any on-chain contract that uses `signer_account_id()` for authorization**.

### Likelihood Explanation
The attack requires:
1. The relayer to hold a balance in a contract that uses `signer_account_id()` for authorization (common in DeFi contracts, staking wrappers, or any contract that tracks deposits by original signer).
2. Alice to know which contract to target (observable on-chain).
3. Alice to craft a valid `DelegateAction` calling that contract's withdrawal/transfer method.

All three conditions are achievable by an unprivileged user with no special access. General-purpose relayers serving many users are at highest risk, as they are more likely to hold balances in various contracts.

### Recommendation
1. **Document the risk explicitly**: Relayers must be advised that their `signer_account_id` is visible to all contracts invoked by inner actions. Relayer accounts should be single-purpose and must not hold balances in contracts that use `signer_account_id()` for authorization.
2. **Consider replacing `signer_id` in inner receipts**: For meta-transactions, the inner receipt's `signer_id` could be set to the `sender_id` (Alice) rather than the relayer, since the relayer's role is purely economic (gas payment). This would prevent the relayer's identity from being exposed to untrusted contract code. This is a protocol-level change requiring a NEP.
3. **Warn in the meta-transaction documentation** alongside the existing balance-refund warning.

### Proof of Concept
1. Relayer `R` holds 100 NEAR deposited in contract `C` which tracks balances by `signer_account_id()` and allows `withdraw()` to send funds to any address when called by the registered signer.
2. Alice creates a `DelegateAction` with `receiver_id = C`, `actions = [FunctionCall("withdraw", args={to: alice})]`, signs it with her key.
3. Alice sends the `SignedDelegateAction` to relayer `R` (off-chain).
4. `R` wraps it in a transaction and submits it on-chain.
5. `apply_delegate_action` creates an inner receipt with `signer_id = R`.
6. Contract `C` executes `withdraw()`, calls `signer_account_id()`, gets `R`, finds R's 100 NEAR balance, and transfers it to Alice.
7. Relayer `R` loses 100 NEAR from contract `C` without consent. [6](#0-5) [2](#0-1) [3](#0-2)

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

**File:** runtime/runtime/src/function_call.rs (L256-262)
```rust
    let context = VMContext {
        current_account_id: runtime_ext.account_id().clone(),
        signer_account_id: action_receipt.signer_id().clone(),
        signer_account_pk: borsh::to_vec(&action_receipt.signer_public_key())
            .expect("Failed to serialize"),
        predecessor_account_id: predecessor_id.clone(),
        refund_to_account_id: action_receipt.refund_to().as_ref().unwrap_or(predecessor_id).clone(),
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L690-704)
```rust
    pub fn signer_account_id(&mut self, register_id: u64) -> Result<()> {
        self.result_state.gas_counter.pay_base(base)?;

        if self.context.is_view() {
            return Err(HostError::ProhibitedInView {
                method_name: "signer_account_id".to_string(),
            }
            .into());
        }
        self.registers.set(
            &mut self.result_state.gas_counter,
            &self.config.limit_config,
            register_id,
            self.context.signer_account_id.as_bytes(),
        )
```

**File:** docs/RuntimeSpec/Actions.md (L363-366)
```markdown
### Outcomes

- All actions inside `delegate_action.actions` are submitted with the `delegate_action.sender_id` as the predecessor, `delegate_action.receiver_id` as the receiver, and the relayer (predecessor of `DelegateAction`) as the signer.
- All gas and balance costs for submitting `delegate_action.actions` are subtracted from the relayer.
```

**File:** docs/architecture/how/meta-tx.md (L236-242)
```markdown
The relayer can see what the cost will be before submitting the meta transaction
and agrees to pay for it, so nothing wrong so far. But what if the transaction
fails execution on Bob's shard? At this point, the predecessor is `Alice` and
therefore she receives the token balance refunded, not the relayer. This is
something relayer implementations must be aware of since there is a financial
incentive for Alice to submit meta transactions that have high balances attached
but will fail on Bob's shard.
```
