### Title
Caller Deposit Permanently Stuck in WalletContract When Intermediate Callbacks Return Early Without Refund - (File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs)

### Summary

The `near-wallet-contract` (the on-chain Ethereum-compatible wallet deployed for eth-implicit accounts) accepts NEAR token deposits from external callers via `rlp_execute`. When the execution path routes through `address_check_callback` or `nep_141_storage_balance_callback`, multiple early-return branches return `PromiseOrValue::Value(...)` without refunding the tracked `CallerDeposit`. Because these callbacks succeed at the NEAR runtime level (they do not panic), the runtime does not issue an automatic deposit refund. The caller's tokens are permanently locked inside the wallet contract with no recovery path.

### Finding Description

`rlp_execute` is `#[payable]` and credits any attached deposit to the wallet contract's balance. The `CallerDeposit` struct is constructed in `inner_rlp_execute` to track the external caller's deposit so it can be manually returned if the downstream cross-contract call fails. [1](#0-0) 

The only place where `CallerDeposit` is correctly refunded is inside `rlp_execute_callback`, on the `PromiseResult::Failed` branch: [2](#0-1) 

However, two intermediate callbacks — `address_check_callback` and `nep_141_storage_balance_callback` — contain multiple early-return branches that return `PromiseOrValue::Value(ExecuteResponse { ... })` **without** issuing any refund transfer for `caller_deposit`:

**`address_check_callback` — four unrefunded early-return paths:** [3](#0-2) [4](#0-3) 

**`nep_141_storage_balance_callback` — four unrefunded early-return paths:** [5](#0-4) [6](#0-5) 

When any of these branches executes, the callback receipt completes successfully (no panic), so the NEAR runtime does not generate a deposit refund receipt. The `caller_deposit` amount remains in the wallet contract's balance with no mechanism to retrieve it.

### Impact Explanation

An external caller who attaches NEAR tokens to `rlp_execute` for an ERC-20 transfer or an EOA base-token transfer with address-check loses those tokens permanently if any of the intermediate callback failure branches fires. The corrupted protocol value is the caller's NEAR balance: it is debited from the caller and credited to the wallet contract, but never returned. There is no retry mechanism and no admin recovery path — the wallet contract has no sweep or rescue function.

### Likelihood Explanation

The trigger requires an external factor to cause the intermediate call to fail or return unexpected data:

- For `address_check_callback`: the address registrar contract (`ADDRESS_REGISTRAR_ACCOUNT_ID`) returns `PromiseResult::Failed` (e.g., the registrar is temporarily unavailable, runs out of gas, or panics), or returns data that cannot be deserialized as `Option<AccountId>`.
- For `nep_141_storage_balance_callback`: the NEP-141 token contract's `storage_balance_of` returns `PromiseResult::Failed`, or returns data that cannot be deserialized as `Option<StorageBalance>`.

Both registrar and arbitrary NEP-141 token contracts are external dependencies. A malicious or buggy token contract can trivially cause `storage_balance_of` to panic. A user who is tricked into using a malicious token contract as the `target` of an ERC-20 transfer will lose their deposit. Even with a legitimate token contract, transient network conditions or gas exhaustion can cause the call to fail. This is directly analogous to the Stargate report's "swap data gets outdated" trigger — an external condition causes the second step to fail after the first step (token receipt) has already committed. [7](#0-6) 

### Recommendation

Every early-return branch in `address_check_callback` and `nep_141_storage_balance_callback` that does not proceed to `rlp_execute_callback` must explicitly refund `caller_deposit` before returning. A helper function mirroring the refund logic in `rlp_execute_callback` should be extracted and called at each such site:

```rust
fn refund_caller_deposit(caller_deposit: Option<CallerDeposit>) {
    if let Some(CallerDeposit { account_id, yocto_near }) = caller_deposit {
        let refund_promise = env::promise_batch_create(&account_id);
        env::promise_batch_action_transfer(
            refund_promise,
            NearToken::from_yoctonear(yocto_near.into()),
        );
    }
}
```

This must be called before every `return PromiseOrValue::Value(...)` in both intermediate callbacks.

### Proof of Concept

1. Attacker deploys a malicious NEP-141 token contract whose `storage_balance_of` method always panics.
2. Victim (external caller) is induced to call `rlp_execute` on their eth-implicit wallet contract with `deposit = 10 NEAR`, encoding an ERC-20 transfer to the malicious token contract as the target.
3. `inner_rlp_execute` constructs `caller_deposit = Some(CallerDeposit { account_id: victim, yocto_near: 10e24 })` and schedules `storage_balance_of` → `nep_141_storage_balance_callback`.
4. The malicious token contract panics on `storage_balance_of`; `nep_141_storage_balance_callback` receives `PromiseResult::Failed` and executes the early-return at line 204–209 — returning `PromiseOrValue::Value(ExecuteResponse { success: false, ... })` without issuing any transfer back to the victim.
5. The callback receipt completes successfully at the NEAR runtime level; no automatic deposit refund is generated.
6. The victim's 10 NEAR is permanently credited to the wallet contract's balance with no recovery path. [8](#0-7)

### Citations

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L141-158)
```rust
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L161-188)
```rust
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
        } else {
            // We must increment the nonce at this point to prevent replay of the transaction.
            // Recall that the nonce was not incremented in `inner_rlp_execute` in the case that
            // the registrar contract was called (i.e. in the case we end up inside this callback).
            self.nonce = self.nonce.saturating_add(1);
            let ext =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            match action_to_promise(target, action)
                .map(|p| p.then(ext.rlp_execute_callback(caller_deposit)))
            {
                Ok(p) => p,
                Err(e) => {
                    return PromiseOrValue::Value(e.into());
                }
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L194-219)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L243-253)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L433-457)
```rust
        TransactionKind::EthEmulation(EthEmulationKind::ERC20Transfer { receiver_id, .. }) => {
            // In the case of the emulated ERC-20 transfer, the receiving account
            // might not be registered with the NEP-141 contract (per the NEP-145)
            // storage standard. Therefore we must create a multi-step promise where
            // first we check if the receiver is registered and then if not call
            // `storage_deposit` in addition to `ft_transfer`.
            let token_id = target;
            let callback_gas = NEP_141_STORAGE_BALANCE_CALLBACK_GAS.saturating_add(action.gas());
            let ext: WalletContractExt =
                WalletContract::ext(current_account_id).with_static_gas(callback_gas);
            let storage_balance_args =
                format!(r#"{{"account_id": "{}"}}"#, receiver_id.as_str()).into_bytes();
            Promise::new(token_id.clone())
                .function_call(
                    "storage_balance_of".into(),
                    storage_balance_args,
                    NearToken::from_yoctonear(0),
                    NEP_141_STORAGE_BALANCE_OF_GAS,
                )
                .then(ext.nep_141_storage_balance_callback(
                    token_id,
                    receiver_id,
                    action,
                    caller_deposit,
                ))
```
