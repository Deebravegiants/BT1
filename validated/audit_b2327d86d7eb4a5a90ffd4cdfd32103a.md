This confirms the analog. `validate_delegate_action_key` (`runtime/runtime/src/actions.rs:563`) checks the access key's receiver/method/deposit restrictions but never calls `check_and_compute_new_allowance` (`runtime/runtime/src/verifier.rs:240`) — the allowance-cap logic that's applied on the direct-transaction path (`verify_and_charge_tx_ephemeral`, `runtime/runtime/src/verifier.rs:322`). This is explicitly acknowledged in the docs as the same class of issue described in the Frax report: a privileged "fast path" (here, the meta-transaction/relayer path) that executes actions against a function-call access key while skipping one of the resource-limiting checks (`allowance`) that the normal path enforces.

### Title
Function-call access key allowance limit is not enforced on the meta-transaction (`DelegateAction`) execution path - (File: `runtime/runtime/src/actions.rs`)

### Summary
A `FunctionCallPermission` access key restricts a key to a specific receiver, specific methods, and (optionally) a finite `allowance` of NEAR that may be spent through it. On the direct-transaction path, `verify_and_charge_tx_ephemeral` enforces all three restrictions, including decrementing/rejecting on `allowance` via `check_and_compute_new_allowance`. On the meta-transaction path, when the same access key signs a `DelegateAction`, `validate_delegate_action_key` re-checks receiver/method/deposit restrictions but never checks or decrements `allowance` at all, because all fees are paid by the relayer instead of the key owner. This is the same bug class as the Frax report: a secondary, less-checked path bypasses a resource/authorization cap that the primary path enforces.

### Finding Description
- Direct path: `verify_and_charge_tx_ephemeral` (`runtime/runtime/src/verifier.rs:269-361`) calls `check_and_compute_new_allowance` (`runtime/runtime/src/verifier.rs:240`), which fails the transaction with `NotEnoughAllowance` once the key's configured spending cap is exceeded. [1](#0-0) 
- Meta-transaction path: `apply_delegate_action` (`runtime/runtime/src/actions.rs`) calls `validate_delegate_action_key` (`runtime/runtime/src/actions.rs:563-712`) which validates nonce, receiver, method name, and deposit — but has no call to `check_and_compute_new_allowance` or any allowance bookkeeping at all. [2](#0-1) 
- This is by-design documented behavior, explicitly acknowledged in the architecture docs as a way to circumvent the allowance limit via a relayer: [3](#0-2) 
- The function-call access key model exists specifically so an account owner can hand out a scoped, spending-capped credential (receiver + methods + allowance) to a third party/app without exposing a full-access key. `allowance` is the *only* field that limits how much value that credential can move; receiver/method restrict *where*, not *how much*.

### Impact Explanation
Because the allowance check is entirely absent on the delegate/meta-transaction path, a holder of a function-call key that was deliberately capped to a very small allowance (e.g., to limit blast radius if the key/app is compromised) can have unlimited value moved through that key by simply routing calls through any relayer (including a colluding or compromised one), since the relayer — not the allowance — funds the calls. This defeats the account owner's intended risk boundary for that key, matching the report's core failure mode ("custodian's ability to limit the scope of an attack" is reduced) even though here the actor initiating the bypass is the compromised/malicious holder of the restricted key itself, not a validator or node operator.

### Likelihood Explanation
High: this requires no protocol feature gate, no special privileges, and no race condition — any account holding a `FunctionCallPermission` key with `allowance: Some(_)` can immediately have any relayer wrap its calls in a `DelegateAction` to bypass the allowance limit. The behavior is deterministic and already demonstrated/acknowledged in the repository's own documentation and is exercised in tests such as `meta_tx_fn_call_access_key_insufficient_allowance`. [4](#0-3) 

### Recommendation
- Short term: decide explicitly whether `allowance` should apply to meta-transaction execution. If it should, add an allowance check/decrement to `validate_delegate_action_key` (or a caller) mirroring `check_and_compute_new_allowance`, tracking spend against the same access-key field even though the relayer pays the gas/deposit. If it should not (current stance, since the relayer pays), update documentation/user-facing guidance to make unambiguously clear that `allowance` on function-call keys is *not* a hard cap when the key can be used via relayers, and consider adding an explicit "delegatable" flag on the access key permission so key issuers can opt out of relayer-based bypass for sensitive keys.
- Long term: audit all constraints attached to `AccessKeyPermission`/`FunctionCallPermission` (receiver, methods, allowance, and any future ones) to confirm they are enforced consistently across every code path that can execute actions under that key (direct tx, `DelegateAction`/`DelegateV2`, gas-key variants), not just the primary transaction-verification path.

### Proof of Concept
1. Account `alice` grants a `FunctionCallPermission` access key to app `bob` with `receiver_id = "token.near"`, `method_names = ["transfer"]`, and `allowance = 1 yoctoNEAR` (intending `bob` to be able to make at most a trivial number of calls before needing alice to top up the allowance).
2. `bob`'s key is compromised, or `bob` decides to abuse it. Instead of signing a normal `SignedTransaction` (which would fail `NotEnoughAllowance` after the first call), `bob` wraps the `transfer` `FunctionCall` action in a `DelegateAction` (`sender_id = alice`) and has any relayer sign/submit the outer transaction.
3. `validate_delegate_action_key` validates receiver/method/nonce and passes; `apply_delegate_action` spawns the receipt with the relayer paying all fees. [5](#0-4) 
4. `bob` repeats step 2 indefinitely through the relayer, executing an unbounded number of `transfer` calls under `alice`'s restricted key, even though `allowance` was set to permit essentially none — the allowance field is never consulted on this path.

### Citations

**File:** runtime/runtime/src/verifier.rs (L322-330)
```rust
    let new_allowance = match check_and_compute_new_allowance(
        access_key,
        account_id,
        tx.public_key(),
        total_cost,
    ) {
        Ok(a) => a,
        Err(e) => return TxVerdict::Failed(e),
    };
```

**File:** runtime/runtime/src/actions.rs (L483-516)
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
```

**File:** runtime/runtime/src/actions.rs (L654-702)
```rust
    // The restriction of "function call" access keys:
    // the transaction must contain the only `FunctionCall` if "function call" access key is used
    if let Some(function_call_permission) = access_key.permission.function_call_permission() {
        if actions.len() != 1 {
            result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                InvalidAccessKeyError::RequiresFullAccess,
            )
            .into());
            return Ok(());
        }
        if let Some(Action::FunctionCall(function_call)) = actions.get(0) {
            if function_call.deposit > Balance::ZERO {
                result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                    InvalidAccessKeyError::DepositWithFunctionCall,
                )
                .into());
                // Before this fix, the missing early return allowed execution
                // to fall through to the receiver_id and method_name checks,
                // which could overwrite this error with a different one.
                if ProtocolFeature::FixDelegateActionDepositWithFunctionCallError
                    .enabled(apply_state.current_protocol_version)
                {
                    return Ok(());
                }
            }
            if delegate_action.receiver_id() != &function_call_permission.receiver_id {
                result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                    InvalidAccessKeyError::ReceiverMismatch {
                        tx_receiver: delegate_action.receiver_id().clone(),
                        ak_receiver: function_call_permission.receiver_id.clone(),
                    },
                )
                .into());
                return Ok(());
            }
            if !function_call_permission.method_names.is_empty()
                && function_call_permission
                    .method_names
                    .iter()
                    .all(|method_name| &function_call.method_name != method_name)
            {
                result.result = Err(ActionErrorKind::DelegateActionAccessKeyError(
                    InvalidAccessKeyError::MethodNameMismatch {
                        method_name: function_call.method_name.clone(),
                    },
                )
                .into());
                return Ok(());
            }
```

**File:** docs/architecture/how/meta-tx.md (L244-266)
```markdown
## Function access keys in meta transactions

Assume alice sends a meta transaction and signs with a function access key.
How exactly are permissions applied in this case?

Function access keys can limit the allowance, the receiving contract, and the
contract methods. The allowance limitation acts slightly strange with meta
transactions.

But first, both the methods and the receiver will be checked as expected. That
is, when the delegate action is unwrapped on Alice's shard, the access key is
loaded from the DB and compared to the function call. If the receiver or method
is not allowed, the function call action fails.

For allowance, however, there is no check. All costs have been covered by the
relayer. Hence, even if the allowance of the key is insufficient to make the call
directly, indirectly through meta transaction it will still work.

This behavior is in the spirit of allowance limiting how much financial
resources the user can use from a given account. But if someone were to limit a
function access key to one trivial action by setting a very small allowance,
that is circumventable by going through a relayer. An interesting twist that
comes with the addition of meta transactions.
```

**File:** integration-tests/src/tests/features/delegate_action.rs (L392-423)
```rust
/// Call a function in a meta tx where the user only has access through a
/// function call access that has too little allowance left.
#[test]
fn meta_tx_fn_call_access_key_insufficient_allowance() {
    let sender = bob_account();
    let relayer = alice_account();
    let receiver = carol_account();

    // 1 yocto near, that's less than 1 gas unit
    let initial_allowance = Balance::from_yoctonear(1);
    let signer = create_user_test_signer(&sender);

    let node = setup_with_access_key(
        &relayer,
        &receiver,
        &sender,
        signer.public_key(),
        initial_allowance,
        TEST_METHOD,
    );

    let actions = vec![log_something_fn_call()];
    // this should still succeed because we use the gas of the relayer, not of the access key
    let outcome = check_meta_tx_fn_call(
        &node,
        actions,
        TEST_METHOD_LEN,
        Balance::ZERO,
        sender,
        relayer,
        receiver,
    );
```
