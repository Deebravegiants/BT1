## Title
Request State Deleted Before Promise Outcome is Known in `confirm()` — Unrecoverable Loss of Multisig-Approved Requests on Receipt Failure - (`multisig/src/lib.rs`)

### Summary
In `MultiSigContract::confirm`, once the confirmation threshold is reached, the request and its confirmations are permanently removed from contract state via `remove_request()` *before* the resulting `Promise`/receipt is known to succeed. If the promise's actions later fail asynchronously (e.g. `Transfer` to a nonexistent/blackholed account, insufficient balance, or a `FunctionCall` action that panics), the multisig request is unrecoverably gone with no way to re-execute it.

### Finding Description
`confirm()` at [1](#0-0)  checks confirmation count, and if the threshold is met, calls `self.remove_request(request_id)` — which deletes both the `requests` and `confirmations` `UnorderedMap` entries and decrements `num_requests_pk` — and only afterwards calls `self.execute_request(request)`, which returns a `PromiseOrValue<bool>` scheduling the actual cross-contract receipt.

`execute_request` at [2](#0-1)  builds a `Promise` chain (e.g. `promise.transfer(amount.into())` for `Transfer` actions) but has no `.then()` callback to check the promise's result and restore state on failure. The contract itself documents this as a known limitation via the comment directly in the code: "If the tx execution fails for any reason, the request and confirmations are removed already, so the client has to start all over" at [3](#0-2) .

Because NEAR promise execution/receipt processing happens asynchronously in a later block, and `remove_request` runs synchronously in the same receipt as `confirm()`, the contract state committing (deletion) always happens regardless of whether the scheduled action later succeeds or fails on-chain.

### Impact Explanation
This matches the "Critical — Permanent freezing, unrecoverable lock, or irrevocable loss of ... multisig request execution flows" category. A legitimately multisig-approved transfer or function call that fails at the receipt level (e.g. transferring to an account that gets deleted between confirmations, a `FunctionCall` action with insufficient gas/deposit causing a panic, or any other receipt-level failure) results in permanent loss of the request: signers must recreate and re-collect all N confirmations from scratch, and in the case of a `Transfer` whose funds are asynchronously non-refundable, the intended action can never be redone from the deleted request state itself.

### Likelihood Explanation
This requires no privileged access — it's the normal multisig approval flow. Any of the co-signers submitting a legitimate request (e.g. a `Transfer` to an account that no longer exists, or is otherwise invalid at execution time) followed by threshold confirmations will trigger this deterministically. It's a straightforward design flaw rather than a contrived edge case, and is already flagged by an in-code comment acknowledging the issue.

### Recommendation
Do not delete request/confirmation state before the promise outcome is known. Options:
- Chain `execute_request`'s promise with a `.then()` callback (`Promise::then`) to a private method that checks `env::promise_result(0)` and only calls `remove_request` on success, restoring/keeping the request on failure.
- Alternatively, mark the request as "executing"/locked instead of deleting it, and finalize removal only in the callback upon success.

### Proof of Concept
1. Signer A calls `add_request` with a `MultiSigRequest { receiver_id: <account that will not exist / becomes invalid>, actions: [Transfer { amount }] }`.
2. Signers confirm via `confirm(request_id)` until `confirmations.len() + 1 >= num_confirmations`.
3. On the threshold-reaching call, `confirm()` executes `remove_request(request_id)` at [4](#0-3) , which deletes `self.requests` and `self.confirmations` entries synchronously, then calls `execute_request(request)` which schedules a `Promise::transfer`.
4. If the receiver account does not exist (or the transfer/function-call receipt otherwise fails), the promise fails asynchronously in a later receipt with no effect on already-committed state.
5. Post-condition: `requests.len() == 0` and `confirmations` has no entry for that id — confirmed independent of the promise's eventual success or failure, matching the described invariant violation.

### Citations

**File:** multisig/src/lib.rs (L167-244)
```rust
    fn execute_request(&mut self, request: MultiSigRequest) -> PromiseOrValue<bool> {
        let mut promise = Promise::new(request.receiver_id.clone());
        let receiver_id = request.receiver_id.clone();
        let num_actions = request.actions.len();
        for action in request.actions {
            promise = match action {
                MultiSigRequestAction::Transfer { amount } => promise.transfer(amount.into()),
                MultiSigRequestAction::CreateAccount => promise.create_account(),
                MultiSigRequestAction::DeployContract { code } => {
                    promise.deploy_contract(code.into())
                }
                MultiSigRequestAction::AddKey {
                    public_key,
                    permission,
                } => {
                    self.assert_self_request(receiver_id.clone());
                    if let Some(permission) = permission {
                        promise.add_access_key(
                            public_key.into(),
                            permission
                                .allowance
                                .map(|x| x.into())
                                .unwrap_or(DEFAULT_ALLOWANCE),
                            permission.receiver_id,
                            permission.method_names.join(",").into_bytes(),
                        )
                    } else {
                        // wallet UI should warn user if receiver_id == env::current_account_id(), adding FAK will render multisig useless
                        promise.add_full_access_key(public_key.into())
                    }
                }
                MultiSigRequestAction::DeleteKey { public_key } => {
                    self.assert_self_request(receiver_id.clone());
                    let pk: PublicKey = public_key.into();
                    // delete outstanding requests by public_key
                    let request_ids: Vec<u32> = self
                        .requests
                        .iter()
                        .filter(|(_k, r)| r.signer_pk == pk)
                        .map(|(k, _r)| k)
                        .collect();
                    for request_id in request_ids {
                        // remove confirmations for this request
                        self.confirmations.remove(&request_id);
                        self.requests.remove(&request_id);
                    }
                    // remove num_requests_pk entry for public_key
                    self.num_requests_pk.remove(&pk);
                    promise.delete_key(pk)
                }
                MultiSigRequestAction::FunctionCall {
                    method_name,
                    args,
                    deposit,
                    gas,
                } => promise.function_call(
                    method_name.into_bytes(),
                    args.into(),
                    deposit.into(),
                    gas.into(),
                ),
                // the following methods must be a single action
                MultiSigRequestAction::SetNumConfirmations { num_confirmations } => {
                    self.assert_one_action_only(receiver_id, num_actions);
                    self.num_confirmations = num_confirmations;
                    return PromiseOrValue::Value(true);
                }
                MultiSigRequestAction::SetActiveRequestsLimit {
                    active_requests_limit,
                } => {
                    self.assert_one_action_only(receiver_id, num_actions);
                    self.active_requests_limit = active_requests_limit;
                    return PromiseOrValue::Value(true);
                }
            };
        }
        promise.into()
    }
```

**File:** multisig/src/lib.rs (L248-266)
```rust
    pub fn confirm(&mut self, request_id: RequestId) -> PromiseOrValue<bool> {
        self.assert_valid_request(request_id);
        let mut confirmations = self.confirmations.get(&request_id).unwrap();
        assert!(
            !confirmations.contains(&env::signer_account_pk()),
            "Already confirmed this request with this key"
        );
        if confirmations.len() as u32 + 1 >= self.num_confirmations {
            let request = self.remove_request(request_id);
            /********************************
            NOTE: If the tx execution fails for any reason, the request and confirmations are removed already, so the client has to start all over
            ********************************/
            self.execute_request(request)
        } else {
            confirmations.insert(env::signer_account_pk());
            self.confirmations.insert(&request_id, &confirmations);
            PromiseOrValue::Value(true)
        }
    }
```
