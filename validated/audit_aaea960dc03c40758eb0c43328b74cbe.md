### Title
Attached NEAR deposit is silently discarded (not forwarded, not refunded) for `AddKey`/`DeleteKey` transactions in the Wallet Contract's `rlp_execute` - ([File: runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs])

### Summary
`WalletContract::rlp_execute` is a `#[payable]` entry point that accepts an attached NEAR deposit meant to accompany an Ethereum-encoded action [1](#0-0) . The deposit is tracked in a `CallerDeposit` struct so it can be refunded to the external caller if the resulting cross-contract promise fails [2](#0-1) , and the refund is only issued from `rlp_execute_callback` when `PromiseResult::Failed` is observed [3](#0-2) . However, `Action::try_into_near_action` only forwards the ETH-tx-derived `additional_value` (the deposit) into the NEAR action for `FunctionCall` and `Transfer`; for `AddKey` and `DeleteKey` the `additional_value` parameter is completely ignored [4](#0-3) . Because `AddKeyAction`/`DeleteKeyAction` on NEAR carry no `deposit` field, any attached deposit accompanying such an action is never attached to any outgoing promise, and—since the resulting promise succeeds—the `CallerDeposit`-based refund path in `rlp_execute_callback` never triggers. The deposit is simply absorbed into the wallet contract's own account balance with no way for the caller to recover it.

### Finding Description
This mirrors the Derby `XChainController` bug class: funds attached to a call are intended to cover an operation, but under a particular code branch (there: `getVaultChainIdOff` returning false; here: the action being `AddKey`/`DeleteKey`) the funds are not forwarded to the intended use and there is no fallback that returns them to the caller.

Root cause chain in nearcore:
1. `rlp_execute` is `#[payable]`, so the caller can attach an arbitrary NEAR deposit [1](#0-0) .
2. `CallerDeposit::new` records this deposit against the predecessor only for the purpose of refunding it on a failed promise [5](#0-4)  and `inner_rlp_execute` constructs this tracker from `env::attached_deposit()` [6](#0-5) .
3. The parsed Ethereum `value` field is converted into `additional_value` and passed to `Action::try_into_near_action` [7](#0-6) .
4. For `Action::FunctionCall` and `Action::Transfer`, `additional_value` is added into the NEAR action's `deposit` field so it is forwarded on-chain [8](#0-7) . For `Action::AddKey` and `Action::DeleteKey`, `additional_value` is never referenced—the produced `near_action::Action::AddKey`/`DeleteKey` carries no deposit at all [9](#0-8) .
5. Because the resulting promise (add/delete key on the wallet's own account) will typically succeed, `rlp_execute_callback` takes the `PromiseResult::Successful` branch and never issues the `CallerDeposit` refund transfer that only exists in the `PromiseResult::Failed` branch [3](#0-2) .

The net effect: any NEAR attached to `rlp_execute` alongside an ABI-encoded `AddKey`/`DeleteKey` transaction is permanently credited to the wallet contract account with no mechanism to reclaim it, exactly the "funds attached to cover an operation get frozen/absorbed when the specific code branch doesn't use them" pattern described in the report.

### Impact Explanation
The `CallerDeposit` test suite confirms deposits are refunded only on call failure, and are otherwise retained by the receiving account regardless of whether the action needed the deposit [10](#0-9) . This is a genuine loss-of-funds condition for whichever account submits/pays for an `rlp_execute` call carrying a nonzero ETH-encoded `value` alongside an `AddKey`/`DeleteKey` payload: the deposit is unconditionally and irreversibly absorbed by the wallet contract's own balance, an unauthorized balance change from the caller's perspective with no compensating refund path. Since the Wallet Contract is a production NEP-141/EVM-emulation bridge contract shipped as part of nearcore's `near-wallet-contract` implementation, this is reachable from any external account submitting a standard RLP-encoded Ethereum transaction through `rlp_execute`.

### Likelihood Explanation
Reachability requires only a normal `rlp_execute` call with the relevant ABI selector (`ADD_KEY_SELECTOR`/`DELETE_KEY_SELECTOR`) and a nonzero `tx.value`, both of which are user-controlled and not rejected by any validation in `validate_tx_value` (which only checks an upper bound, not that `value == 0` for these action kinds) [11](#0-10) . No special privileges or malicious-node/validator role is needed—any unprivileged caller (or a relayer misconfigured to attach a deposit) can trigger this loss.

### Recommendation
Either reject `rlp_execute` calls whose ABI-decoded `value` is nonzero when the parsed action is `AddKey`/`DeleteKey` (since these NEAR actions cannot carry a deposit), or explicitly refund the `additional_value` portion of the attached deposit back to the predecessor when constructing `Action::AddKey`/`Action::DeleteKey` in `try_into_near_action`, mirroring the existing `CallerDeposit` refund mechanism used for failed promises.

### Proof of Concept
1. A user encodes an Ethereum transaction whose calldata matches `ADD_KEY_SELECTOR` (or `DELETE_KEY_SELECTOR`) with the `to` address equal to the wallet's own address (`TargetKind::CurrentAccount`), targeting `SelfNearNativeAction` handling [12](#0-11) , but sets the Ethereum `value` field to a nonzero amount.
2. A relayer (or the user) calls `rlp_execute(target, tx_bytes_b64)` attaching a NEAR deposit equal to (or proportional to) that `value` via `#[payable]`.
3. `inner_rlp_execute` parses the action as `Action::AddKey`/`Action::DeleteKey`, computes `additional_value` from `tx.value`, but `try_into_near_action` drops it silently [9](#0-8) .
4. The `AddKey`/`DeleteKey` promise executes successfully; `rlp_execute_callback` sees `PromiseResult::Successful` and returns without refunding the `CallerDeposit` [13](#0-12) .
5. The attached NEAR remains permanently credited to the wallet contract's account balance; the caller has no way to reclaim it.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-93)
```rust
    #[payable]
    pub fn rlp_execute(
        &mut self,
        target: AccountId,
        tx_bytes_b64: String,
    ) -> PromiseOrValue<ExecuteResponse> {
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-316)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L340-345)
```rust
    let context = ExecutionContext::new(
        current_account_id.clone(),
        predecessor_account_id,
        env::attached_deposit(),
    )?;
    let caller_deposit = CallerDeposit::new(&context);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L172-192)
```rust
/// A data type to keep track of the deposit given by an external caller.
/// This allows us to refund the caller's deposit if the cross-contract call fails.
#[derive(Debug, PartialEq, Eq, Clone, serde::Serialize, serde::Deserialize)]
pub struct CallerDeposit {
    pub account_id: AccountId,
    pub yocto_near: NonZeroU128,
}

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L238-296)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L159-166)
```rust
    validate_tx_value(&tx)?;

    // Call to `low_u128` here is safe because of the validation done in `validate_tx_value`
    let near_action = action
        .try_into_near_action(tx.value.raw().low_u128().saturating_mul(MAX_YOCTO_NEAR.into()))?;

    Ok((near_action, transaction_kind))
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L272-304)
```rust
        ADD_KEY_SELECTOR => {
            let (
                public_key_kind,
                public_key,
                nonce,
                is_full_access,
                is_limited_allowance,
                allowance,
                receiver_id,
                method_names,
            ) = ethabi_utils::abi_decode(&ADD_KEY_SIGNATURE, &tx.data[4..])?;
            Ok((
                Action::AddKey {
                    public_key_kind,
                    public_key,
                    nonce,
                    is_full_access,
                    is_limited_allowance,
                    allowance,
                    receiver_id,
                    method_names,
                },
                ParsableTransactionKind::SelfNearNativeAction,
            ))
        }
        DELETE_KEY_SELECTOR => {
            let (public_key_kind, public_key) =
                ethabi_utils::abi_decode(&DELETE_KEY_SIGNATURE, &tx.data[4..])?;
            Ok((
                Action::DeleteKey { public_key_kind, public_key },
                ParsableTransactionKind::SelfNearNativeAction,
            ))
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L370-376)
```rust
fn validate_tx_value(tx: &NormalizedEthTransaction) -> Result<(), Error> {
    if tx.value.raw() > VALUE_MAX {
        return Err(Error::User(UserError::ValueTooLarge));
    }

    Ok(())
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L170-229)
```rust
// An external caller gets its deposit back if the cross-contract call fails.
#[tokio::test]
async fn test_caller_refunds() -> anyhow::Result<()> {
    let TestContext { worker, wallet_contract, wallet_sk, address_registrar, .. } =
        TestContext::new().await?;

    let caller = worker.root_account()?;
    let deposit_amount = NearToken::from_near(3);
    let create_tx = |receiver_id: &AccountId, nonce: u64| {
        let method = "register";
        let args = br#"{"account_id": "birchmd.near"}"#;
        let action = Action::FunctionCall {
            receiver_id: receiver_id.to_string(),
            method_name: method.into(),
            args: args.to_vec(),
            gas: Gas::from_tgas(10).as_gas(),
            yocto_near: 0,
        };
        utils::create_signed_transaction(
            nonce,
            receiver_id,
            Wei::new_u128(deposit_amount.as_yoctonear() / (MAX_YOCTO_NEAR as u128)),
            action,
            &wallet_sk,
        )
    };

    // External caller gets a refund when the cross-contract call fails
    let pre_tx_account_balance = caller.view_account().await?.balance;
    let receiver_id: AccountId = "fake.near".parse()?;
    let result = wallet_contract
        .rlp_execute_from(
            &caller,
            receiver_id.as_str(),
            &create_tx(&receiver_id, 0),
            deposit_amount,
        )
        .await?;
    assert!(!result.success);
    let post_tx_account_balance = caller.view_account().await?.balance;
    assert!(
        pre_tx_account_balance.as_yoctonear() - post_tx_account_balance.as_yoctonear()
            < deposit_amount.as_yoctonear()
    );

    // External caller does not get a refund when their tokens are spent
    let pre_tx_account_balance = post_tx_account_balance;
    let receiver_id = address_registrar.id();
    let result = wallet_contract
        .rlp_execute_from(&caller, receiver_id.as_str(), &create_tx(receiver_id, 1), deposit_amount)
        .await?;
    assert!(result.success);
    let post_tx_account_balance = caller.view_account().await?.balance;
    assert!(
        pre_tx_account_balance.as_yoctonear() - post_tx_account_balance.as_yoctonear()
            >= deposit_amount.as_yoctonear()
    );

    Ok(())
}
```
