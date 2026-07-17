### Title
Attached NEAR Deposit Permanently Absorbed in `WalletContract.rlp_execute` Error Paths Without Refund - (File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs)

### Summary

The `rlp_execute` entry point of `WalletContract` is marked `#[payable]`, allowing any external caller to attach NEAR tokens. However, multiple code paths return a `PromiseOrValue::Value(...)` (a non-promise return) without refunding the attached deposit. In NEAR, a deposit is only automatically refunded when a receipt panics; a normal return absorbs the deposit into the contract's balance. The `CallerDeposit` mechanism exists precisely to handle this, but it is bypassed or ignored in several reachable paths.

### Finding Description

**Root cause 1 — `has_in_flight_tx` early return (no `CallerDeposit` created):**

`rlp_execute` checks `has_in_flight_tx` before `inner_rlp_execute` is ever called, so `CallerDeposit::new` is never reached. Any NEAR attached by an external caller is silently absorbed. [1](#0-0) 

**Root cause 2 — `address_check_callback` error paths ignore `caller_deposit`:**

When the address registrar call fails (`PromiseResult::Failed`), when its response cannot be deserialized, or when the target resolves to an existing named account (non-self-signer path), the function returns `PromiseOrValue::Value(...)` without issuing a refund transfer for `caller_deposit`. [2](#0-1) 

**Root cause 3 — `nep_141_storage_balance_callback` error paths ignore `caller_deposit`:**

When the NEP-141 `storage_balance_of` call fails, when its response cannot be deserialized, or when the action is unexpectedly not a `FunctionCall`, the function returns `PromiseOrValue::Value(...)` without refunding `caller_deposit`. [3](#0-2) 

The `CallerDeposit` type is designed specifically to track and refund external caller deposits on failure: [4](#0-3) 

The only place a refund is correctly issued is in `rlp_execute_callback` on `PromiseResult::Failed`: [5](#0-4) 

All other failure exits omit this refund.

### Impact Explanation

An external caller who attaches NEAR to `rlp_execute` (e.g., to fund a cross-contract call) loses their deposit permanently in any of the above paths. The deposit is absorbed into the ETH-implicit account's balance. The caller's NEAR balance is incorrectly debited; the wallet contract owner's balance is incorrectly credited. The corrupted protocol value is the caller's on-chain NEAR balance as stored in the runtime state trie.

### Likelihood Explanation

The `WalletContract` is deployed as a global contract for all ETH-implicit accounts on NEAR. The `rlp_execute` function is `#[payable]` and the `CallerDeposit` mechanism is explicitly documented and tested for external callers who attach deposits (see `test_caller_refunds`). The `address_check_callback` registrar-failure path and the `nep_141_storage_balance_callback` failure path are reachable whenever the respective cross-contract calls run out of gas or the target contract panics — conditions that can occur in normal operation or be induced by a malicious token contract. The `has_in_flight_tx` path is reachable whenever a second caller attaches NEAR during an in-flight transaction. [6](#0-5) 

### Recommendation

In every `PromiseOrValue::Value(...)` return inside `address_check_callback` and `nep_141_storage_balance_callback`, issue a refund transfer for `caller_deposit` before returning, mirroring the pattern already used in `rlp_execute_callback`. For the `has_in_flight_tx` path in `rlp_execute`, either panic (triggering NEAR's automatic deposit refund) or explicitly transfer `env::attached_deposit()` back to `env::predecessor_account_id()` before returning the error value.

### Proof of Concept

**Path A (`has_in_flight_tx`):**
1. Account A calls `rlp_execute` with a valid Ethereum-signed transaction; `has_in_flight_tx` becomes `true`.
2. Before the in-flight receipts resolve, account B calls `rlp_execute` attaching 1 NEAR.
3. The `has_in_flight_tx` guard fires at line 97, returning `PromiseOrValue::Value(...)`.
4. Account B's 1 NEAR is absorbed into the wallet contract's balance; account B has no recourse.

**Path B (`nep_141_storage_balance_callback` failure):**
1. A malicious NEP-141 token contract is deployed that always panics on `storage_balance_of`.
2. An external caller calls `rlp_execute` with an ERC-20 transfer action targeting this token, attaching NEAR as a deposit.
3. `inner_rlp_execute` schedules `storage_balance_of` → `nep_141_storage_balance_callback`.
4. `storage_balance_of` panics; `nep_141_storage_balance_callback` receives `PromiseResult::Failed`.
5. The callback returns `PromiseOrValue::Value(...)` at line 204–209 without refunding `caller_deposit`.
6. The caller's attached NEAR is absorbed into the wallet contract's balance. [7](#0-6) [8](#0-7)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-104)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L134-173)
```rust
    pub fn address_check_callback(
        &mut self,
        target: AccountId,
        action: near_action::Action,
        caller_deposit: Option<CallerDeposit>,
    ) -> PromiseOrValue<ExecuteResponse> {
        self.has_in_flight_tx = false;
        let maybe_account_id: Option<AccountId> = match env::promise_result(0) {
            PromiseResult::Failed => {
                return PromiseOrValue::Value(ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some("Call to Address Registrar contract failed".into()),
                });
            }
            PromiseResult::Successful(value) => match serde_json::from_slice(&value) {
                Ok(x) => x,
                Err(_) => {
                    return PromiseOrValue::Value(ExecuteResponse {
                        success: false,
                        success_value: None,
                        error: Some("Unexpected response from account registrar".into()),
                    });
                }
            },
        };
        let current_account_id = env::current_account_id();
        let promise = if maybe_account_id.is_some() {
            // We intentionally do not increment the nonce in this case because the
            // error is caused by a faulty relayer, not the user. An honest relayer
            // may still be able to successfully send the user's intended transaction.
            if env::signer_account_id() == current_account_id {
                create_ban_relayer_promise(current_account_id)
            } else {
                return PromiseOrValue::Value(ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some("Invalid target: target is address corresponding to existing named account_id".into()),
                });
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L194-253)
```rust
    #[private]
    pub fn nep_141_storage_balance_callback(
        &mut self,
        token_id: AccountId,
        receiver_id: AccountId,
        action: near_action::Action,
        caller_deposit: Option<CallerDeposit>,
    ) -> PromiseOrValue<ExecuteResponse> {
        self.has_in_flight_tx = false;
        let maybe_storage_balance: Option<StorageBalance> = match env::promise_result(0) {
            PromiseResult::Failed => {
                return PromiseOrValue::Value(ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some(format!("Call to NEP-141 {token_id}::storage_balance_of failed")),
                });
            }
            PromiseResult::Successful(value) => match serde_json::from_slice(&value) {
                Ok(x) => x,
                Err(_) => {
                    return PromiseOrValue::Value(ExecuteResponse {
                        success: false,
                        success_value: None,
                        error: Some("Unexpected response from NEP-141 storage_balance_of".into()),
                    });
                }
            },
        };
        let current_account_id = env::current_account_id();
        let ext = WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
        let promise = match maybe_storage_balance {
            Some(_) => {
                // receiver_id is registered so we can send the transfer
                // without additional actions. Note: in the standard NEP-141
                // implementation it is impossible to have `Some` storage balance,
                // but have it be insufficient to transact.
                match action_to_promise(token_id, action)
                    .map(|p| p.then(ext.rlp_execute_callback(caller_deposit)))
                {
                    Ok(p) => p,
                    Err(e) => {
                        return PromiseOrValue::Value(e.into());
                    }
                }
            }
            None => {
                // receiver_id is not registered so we must call `storage_deposit` first.
                let storage_deposit_args =
                    format!(r#"{{"account_id": "{receiver_id}"}}"#).into_bytes();
                let transfer_function_call = match action {
                    near_action::Action::FunctionCall(x) => x,
                    _ => {
                        return PromiseOrValue::Value(ExecuteResponse {
                            success: false,
                            success_value: None,
                            error: Some(
                                "Expected function call action to perform NEP-141 transfer".into(),
                            ),
                        });
                    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-305)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L172-191)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L170-228)
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
```
