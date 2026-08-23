### Title
Wallet Contract silently drops attached ETH-value on `AddKey`/`DeleteKey` transactions, freezing relayer deposits - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs`)

### Summary
The `near-wallet-contract` (the eth-implicit account "wallet" contract that translates RLP-encoded Ethereum transactions into NEAR actions) accepts a NEAR deposit attached to the payable `rlp_execute` entrypoint that is meant to carry the Ethereum transaction's `value` field through to the resulting NEAR action. For `FunctionCall` and `Transfer` actions this value is correctly folded into the outgoing promise's deposit, but for `AddKey` and `DeleteKey` actions it is silently discarded, exactly mirroring the reported bug class where bridging/plain calls that have no legitimate use for attached native value fail to check or reject non-zero value, causing it to be frozen on the contract's balance instead of being used or refunded.

### Finding Description
`rlp_execute` is `#[payable]` and captures the attached NEAR deposit into `ExecutionContext::attached_deposit`, from which `CallerDeposit::new` records the depositing predecessor for later refund only if the resulting cross-contract promise fails: [1](#0-0) [2](#0-1) 

The Ethereum transaction's `value` field (converted to yoctoNEAR) is passed as `additional_value` into `Action::try_into_near_action`: [3](#0-2) 

Inside `try_into_near_action`, `additional_value` is correctly added to the deposit for `FunctionCall` and `Transfer`, but for `AddKey` and `DeleteKey` it is never referenced at all — those branches build their `near_action::Action` without consuming `additional_value` in any way: [4](#0-3) 

This is reinforced by `Action::value()`, which unconditionally returns zero for `AddKey`/`DeleteKey` regardless of the actual attached value: [5](#0-4) 

Finally, `action_to_promise` builds the outbound `Promise` for `AddKey` (`add_access_key_allowance_with_nonce`) and `DeleteKey` (`delete_key`) with no deposit/transfer component whatsoever: [6](#0-5) 

Because the attached NEAR deposit was already credited to the wallet contract's account balance the instant the `rlp_execute` receipt executed (per NEAR's economics model, `attached_deposit` is deposited before contract execution begins), and because `rlp_execute_callback` only issues a `CallerDeposit` refund when the inner promise result is `PromiseResult::Failed`: [7](#0-6) 

a successful `AddKey`/`DeleteKey` execution leaves the caller's deposit permanently stuck in the wallet contract's balance — never used, never refunded, and never rejected up front. There is no equivalent of the recommended mitigation ("revert when the action has no native use for the attached value") anywhere in `parse_tx_data`, `validate_tx_value`, or `try_into_near_action` for the `SelfNearNativeAction` (`AddKey`/`DeleteKey`) branch.

### Impact Explanation
A relayer (the `predecessor_id` of `rlp_execute`, distinct from the wallet's `current_account_id`) that attaches a NEAR deposit corresponding to a nonzero `value` field in a user's signed `AddKey` or `DeleteKey` Ethereum-style transaction will have that deposit permanently absorbed into the target wallet contract's balance with no path to reclaim it via the wallet contract logic. This matches the "funds frozen on contract balance" impact of the referenced report — unauthorized retention of value that was never intended to be spendable by that account, and loss of funds for the party that attached it (the relayer), since only failure paths trigger a refund.

### Likelihood Explanation
This is reachable by any unprivileged caller/relayer submitting an ordinary `FunctionCall` transaction to `rlp_execute` with a base64-encoded RLP transaction whose calldata selector is `ADD_KEY_SELECTOR` or `DELETE_KEY_SELECTOR` and whose Ethereum `value` field is nonzero, while attaching the corresponding NEAR deposit to the outer call. No validator, malicious-peer, or privileged capability is required — it only requires a relayer/user misconfiguration (accidentally or intentionally including a value in a key-management transaction), which is directly analogous to the "mistakenly sent native funds" scenario in the original report.

### Recommendation
In `Action::try_into_near_action` (and/or in `parse_tx_data`/`validate_tx_value`), reject `AddKey`/`DeleteKey` transactions whose combined value (`tx.value` converted to yoctoNEAR via `additional_value`) is nonzero, returning a `UserError` instead of silently discarding it — mirroring the recommended fix of reverting when a non-value-consuming action receives non-zero attached value. Alternatively, always refund any unused `additional_value` back to the `predecessor_account_id` regardless of whether the inner promise succeeds or fails.

### Proof of Concept
1. A relayer submits `rlp_execute(target = <wallet_account>, tx_bytes_b64 = <RLP tx>)` and attaches, e.g., 1 NEAR as `attached_deposit`.
2. The RLP transaction's calldata begins with `DELETE_KEY_SELECTOR` (`0x3fc6d404`) encoding a valid `public_key_kind`/`public_key`, and the transaction's `value` field is set to a nonzero amount equal to the attached deposit (within `VALUE_MAX`).
3. `parse_rlp_tx_to_action` parses this as `ParsableTransactionKind::SelfNearNativeAction` → `Action::DeleteKey`, then calls `try_into_near_action(additional_value)` where `additional_value > 0`.
4. Per `types.rs:291-296`, `additional_value` is discarded entirely; `near_action::Action::DeleteKey` carries no deposit.
5. `action_to_promise` creates `Promise::new(target).delete_key(public_key)` with zero attached balance; `rlp_execute_callback` observes `PromiseResult::Successful` and returns success without ever refunding the 1 NEAR to the relayer.
6. The 1 NEAR remains part of the wallet contract's account balance, unaccounted for and unrecoverable through the contract's public interface.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-114)
```rust
    #[payable]
    pub fn rlp_execute(
        &mut self,
        target: AccountId,
        tx_bytes_b64: String,
    ) -> PromiseOrValue<ExecuteResponse> {
        // To ensure user actions are executed in the desired order,
        // having multiple transactions in flight at the same time is
        // not allowed.
        if self.has_in_flight_tx {
            return PromiseOrValue::Value(ExecuteResponse {
                success: false,
                success_value: None,
                error: Some(
                    "Error: transaction already in progress, please try again later.".into(),
                ),
            });
        }
        let current_account_id = env::current_account_id();
        let predecessor_account_id = env::predecessor_account_id();
        let result = inner_rlp_execute(
            current_account_id.clone(),
            predecessor_account_id,
            target,
            tx_bytes_b64,
            &mut self.nonce,
        );
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-317)
```rust
        match env::promise_result(0) {
            PromiseResult::Failed => {
                // The cross-contract call failed, refund the caller if needed
                if let Some(CallerDeposit { account_id, yocto_near }) = caller_deposit {
                    let refund_promise = env::promise_batch_create(&account_id);
                    env::promise_batch_action_transfer(
                        refund_promise,
                        NearToken::from_yoctonear(yocto_near.into()),
                    );
                }

                ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some("Failed Near promise".into()),
                }
            }
            PromiseResult::Successful(value) => {
                ExecuteResponse { success: true, success_value: Some(value), error: None }
            }
        }
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L475-501)
```rust
fn action_to_promise(target: AccountId, action: near_action::Action) -> Result<Promise, Error> {
    match action {
        near_action::Action::FunctionCall(action) => Ok(Promise::new(target).function_call(
            action.method_name,
            action.args,
            action.deposit,
            action.gas,
        )),
        near_action::Action::Transfer(action) => Ok(Promise::new(target).transfer(action.deposit)),
        near_action::Action::AddKey(action) => match action.access_key.permission {
            near_action::AccessKeyPermission::FullAccess => {
                Err(Error::User(UserError::UnsupportedAction(UnsupportedAction::AddFullAccessKey)))
            }
            near_action::AccessKeyPermission::FunctionCall(access) => Ok(Promise::new(target)
                .add_access_key_allowance_with_nonce(
                    action.public_key,
                    access.allowance.and_then(Allowance::limited).unwrap_or(Allowance::Unlimited),
                    access.receiver_id,
                    access.method_names.join(","),
                    action.access_key.nonce,
                )),
        },
        near_action::Action::DeleteKey(action) => {
            Ok(Promise::new(target).delete_key(action.public_key))
        }
    }
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L180-192)
```rust
impl CallerDeposit {
    pub fn new(context: &ExecutionContext) -> Option<Self> {
        // Only track for external (non-self) callers
        if context.current_account_id == context.predecessor_account_id {
            return None;
        }

        NonZeroU128::new(context.attached_deposit.as_yoctonear()).map(|yocto_near| Self {
            account_id: context.predecessor_account_id.clone(),
            yocto_near,
        })
    }
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L226-236)
```rust
impl Action {
    pub fn value(&self) -> NearToken {
        match self {
            Action::FunctionCall { yocto_near, .. } => {
                NearToken::from_yoctonear((*yocto_near).into())
            }
            Action::Transfer { yocto_near, .. } => NearToken::from_yoctonear((*yocto_near).into()),
            Action::AddKey { .. } => NearToken::from_yoctonear(0),
            Action::DeleteKey { .. } => NearToken::from_yoctonear(0),
        }
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L238-299)
```rust
    pub fn try_into_near_action(
        self,
        additional_value: u128,
    ) -> Result<near_action::Action, Error> {
        let action = match self {
            Action::FunctionCall { receiver_id: _, method_name, args, gas, yocto_near } => {
                let action = FunctionCallAction {
                    method_name,
                    args,
                    gas: Gas::from_gas(gas),
                    deposit: NearToken::from_yoctonear(
                        additional_value.saturating_add(yocto_near.into()),
                    ),
                };
                near_action::Action::FunctionCall(action)
            }
            Action::Transfer { receiver_id: _, yocto_near } => {
                let action = TransferAction {
                    deposit: NearToken::from_yoctonear(
                        additional_value.saturating_add(yocto_near.into()),
                    ),
                };
                near_action::Action::Transfer(action)
            }
            Action::AddKey {
                public_key_kind,
                public_key,
                nonce,
                is_full_access,
                is_limited_allowance,
                allowance,
                receiver_id,
                method_names,
            } => {
                let public_key = construct_public_key(public_key_kind, &public_key)?;
                let access_key = if is_full_access {
                    AccessKey { nonce, permission: AccessKeyPermission::FullAccess }
                } else {
                    let allowance = if is_limited_allowance { Some(allowance) } else { None };
                    AccessKey {
                        nonce,
                        permission: AccessKeyPermission::FunctionCall(FunctionCallPermission {
                            allowance: allowance.map(NearToken::from_yoctonear),
                            receiver_id: receiver_id
                                .parse()
                                .map_err(|_| Error::User(UserError::InvalidAccessKeyAccountId))?,
                            method_names,
                        }),
                    }
                };
                let action = AddKeyAction { public_key, access_key };
                near_action::Action::AddKey(action)
            }
            Action::DeleteKey { public_key_kind, public_key } => {
                let action = DeleteKeyAction {
                    public_key: construct_public_key(public_key_kind, &public_key)?,
                };
                near_action::Action::DeleteKey(action)
            }
        };
        Ok(action)
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L159-165)
```rust
    validate_tx_value(&tx)?;

    // Call to `low_u128` here is safe because of the validation done in `validate_tx_value`
    let near_action = action
        .try_into_near_action(tx.value.raw().low_u128().saturating_mul(MAX_YOCTO_NEAR.into()))?;

    Ok((near_action, transaction_kind))
```
