Based on my research, I found a valid analog to the reported bug class in the `near-wallet-contract` (the eth-implicit-account emulation contract) shipped as part of nearcore.

### Title
`WalletContract` can become permanently locked (`has_in_flight_tx` stuck `true`) if a promise callback fails before it resets the flag - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
`WalletContract::rlp_execute` enforces a single-in-flight-transaction invariant using the boolean field `has_in_flight_tx`. It is set to `true` right before returning a scheduled promise, and is only ever reset to `false` inside the eventual callback functions (`rlp_execute_callback`, `address_check_callback`, `nep_141_storage_balance_callback`, `ban_relayer`). There is no other path, timeout, or admin/owner recovery function that clears this flag.

### Finding Description
The contract's own doc comment states the invariant explicitly: `has_in_flight_tx` must be `true` while a promise is outstanding and `false` otherwise [1](#0-0) . `rlp_execute` checks this flag at the top and refuses to proceed if it is already `true` [2](#0-1) , then sets it `true` before returning the outgoing `Promise` [3](#0-2) .

The flag is reset to `false` only as the very first statement inside each callback method, e.g. `rlp_execute_callback` [4](#0-3) , `address_check_callback` [5](#0-4) , `nep_141_storage_balance_callback` [6](#0-5) , and `ban_relayer` [7](#0-6) .

On NEAR, a contract's state mutations are only persisted to the trie if the function call completes without panicking; if a `FunctionCall` action fails (e.g. it runs out of attached gas, or panics for any other reason) all state writes made during that execution — including the `self.has_in_flight_tx = false` write at the top of the function — are discarded, and only `PromiseResult::Failed` is recorded for the caller. This is the same failure class as the reported bug: a "boolean status" is only ever cleared inside a callback that is expected to always run to completion, but if that callback itself fails to complete (analogous to GMX's `addLiquidity` being cancelled after `processWithdrawFailure()`), there is no other mechanism in the contract to reset the flag. Once `has_in_flight_tx` is stuck `true`, every future call to `rlp_execute` is permanently rejected with `"transaction already in progress, please try again later."` [8](#0-7) , and there is no owner/admin/reset method anywhere in the contract to clear it (confirmed by searching the file — only the four callback sites touch `has_in_flight_tx`).

A realistic trigger is attaching insufficient gas for the callback relative to the inner action's dynamic gas needs: gas for `rlp_execute_callback` is computed as a fixed constant plus the inner action's `gas()` value supplied by the caller-controlled RLP transaction [9](#0-8) ; if the actual gas consumed by the callback's execution (deserializing `promise_result`, building a refund promise, etc.) exceeds what was attached under adversarial/edge conditions, the callback panics with "Exceeded the prepaid gas" and its state changes (the reset of `has_in_flight_tx`) never commit.

### Impact Explanation
Once triggered, the `WalletContract` instance is permanently denied for all future eth-emulated transactions routed through `rlp_execute` — no user funds routed through this wallet can ever submit another transaction, and there is no recovery path in the contract itself. This matches the report's "unable to withdraw or deposit funds, halting essential interactions" impact class, applied to the NEAR eth-implicit-account wallet instead of a DeFi vault.

### Likelihood Explanation
This requires a specific, somewhat narrow gas-mis-accounting or callback-panic condition (out-of-gas in the callback, or any other panic path reachable from attacker/relayer-supplied `target`/`action`/`tx_bytes_b64` input before the flag-reset line's effects are committed). It is not trivially triggerable on every call, but it is reachable by a malicious or buggy relayer crafting a transaction whose downstream action consumes more gas than budgeted, or by an unexpected panic anywhere in the callback body's control flow (e.g. the "Invariant violation" arithmetic/format paths, or a future code change adding logic after the reset line that panics).

### Recommendation
Do not rely solely on the callback executing successfully to clear `has_in_flight_tx`. Instead:
- Persist the "in-flight" marker in a way that is robust to callback failure, e.g., write it via a low-level promise action (like a guaranteed refund/reset transfer) rather than a state mutation gated on successful callback completion, or
- Add a permissionless "unstick" recovery function (analogous to `afterWithdrawalCancellation` in the report) that lets anyone clear `has_in_flight_tx` once outstanding promises are provably resolved, or
- Ensure callback gas budgets are provably sufficient regardless of caller-supplied `action.gas()` so the callback itself cannot run out of gas before resetting the flag.

### Proof of Concept
Not applicable as a runnable exploit — the concrete PoC requires demonstrating a specific gas-exhaustion or panic condition inside `rlp_execute_callback`/`address_check_callback`/`nep_141_storage_balance_callback` before the `self.has_in_flight_tx = false` write commits (e.g., crafting a relayed `FunctionCall` action whose supplied `action.gas()` under-budgets the callback's actual runtime cost). The existing test `test_simultaneous_transactions` [10](#0-9)  already exercises the "in-flight" guard's happy path and would need to be extended with a forced callback panic/out-of-gas scenario to demonstrate permanent lockout.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L46-55)
```rust
pub struct WalletContract {
    pub nonce: u64,
    /// Tracks whether a transaction is currently being executed
    /// (i.e. has receipts that have not yet resolved).
    /// Invariant: `has_in_flight_tx` must be `true` when a mutable method
    /// of this contract returns a promise and `false` otherwise (except
    /// for the check if a transaction is already in flight at the beginning
    /// of `rlp_execute`).
    pub has_in_flight_tx: bool,
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L93-105)
```rust
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L116-128)
```rust
        match result {
            Ok(promise) => {
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(Error::Relayer(_)) if env::signer_account_id() == current_account_id => {
                let promise = create_ban_relayer_promise(current_account_id);
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(e) => PromiseOrValue::Value(e.into()),
        }
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L134-140)
```rust
    pub fn address_check_callback(
        &mut self,
        target: AccountId,
        action: near_action::Action,
        caller_deposit: Option<CallerDeposit>,
    ) -> PromiseOrValue<ExecuteResponse> {
        self.has_in_flight_tx = false;
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L194-202)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L276-281)
```rust
    pub fn rlp_execute_callback(
        &mut self,
        caller_deposit: Option<CallerDeposit>,
    ) -> ExecuteResponse {
        self.has_in_flight_tx = false;
        let n = env::promise_results_count();
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L319-327)
```rust
    #[private]
    pub fn ban_relayer(&mut self) -> ExecuteResponse {
        self.has_in_flight_tx = false;
        ExecuteResponse {
            success: false,
            success_value: None,
            error: Some("Error: faulty relayer".into()),
        }
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L412-470)
```rust
    let promise = match transaction_kind {
        TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
            address_check: Some(address),
            ..
        }) => {
            let callback_gas = ADDRESS_CHECK_CALLBACK_GAS.saturating_add(action.gas());
            let ext = WalletContract::ext(current_account_id).with_static_gas(callback_gas);
            let address_registrar = {
                let account_id = ADDRESS_REGISTRAR_ACCOUNT_ID
                    .trim()
                    .parse()
                    .unwrap_or_else(|_| env::panic_str("Invalid address registrar"));
                ext_registrar::ext(account_id).with_static_gas(REGISTRAR_LOOKUP_GAS)
            };
            let address = format!("0x{}", hex::encode(address));
            address_registrar.lookup(address).then(ext.address_check_callback(
                target,
                action,
                caller_deposit,
            ))
        }
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
        }
        TransactionKind::EthEmulation(EthEmulationKind::SelfBaseTokenTransfer) => {
            // Base token transfers to self are no-ops on Near, so we do not need to
            // schedule an additional call. We can simply go straight to `rlp_execute_callback`.
            let ext: WalletContractExt =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            ext.rlp_execute_callback(caller_deposit)
        }
        _ => {
            let ext =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            action_to_promise(target, action)?.then(ext.rlp_execute_callback(caller_deposit))
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L121-168)
```rust
/// Only one transaction can be in flight at a time.
#[tokio::test]
async fn test_simultaneous_transactions() -> anyhow::Result<()> {
    let TestContext { worker, wallet_contract, wallet_sk, .. } = TestContext::new().await?;

    let receiver_account = worker.root_account().unwrap();

    let initial_receiver_balance = receiver_account.view_account().await.unwrap().balance;

    let receiver_id = receiver_account.id().as_str().into();
    let action = Action::Transfer { receiver_id, yocto_near: 1 };
    let signed_transaction =
        utils::create_signed_transaction(0, receiver_account.id(), Wei::zero(), action, &wallet_sk);
    let wallet_method_call_1 = near_workspaces::operations::Function::new("rlp_execute")
        .args_json(serde_json::json!({
            "target": receiver_account.id(),
            "tx_bytes_b64": codec::encode_b64(&codec::rlp_encode(&signed_transaction))
        }))
        .gas(near_workspaces::types::Gas::from_tgas(100));
    let wallet_method_call_2 = near_workspaces::operations::Function::new("rlp_execute")
        .args_json(serde_json::json!({
            "target": receiver_account.id(),
            "tx_bytes_b64": codec::encode_b64(&codec::rlp_encode(&signed_transaction))
        }))
        .gas(near_workspaces::types::Gas::from_tgas(100));

    let near_transaction = wallet_contract
        .inner
        .as_account()
        .batch(wallet_contract.inner.id())
        .call(wallet_method_call_1)
        .call(wallet_method_call_2)
        .transact()
        .await?;

    let result: ExecuteResponse = near_transaction.json()?;

    // The second transaction in the batch fails and this is returned as the
    // result of the Near transaction. But the first transaction in the batch
    // spawns promises that resolve, so the transfer was will successful.
    assert!(!result.success);
    assert!(result.error.unwrap().contains("transaction already in progress"));

    let final_receiver_balance = receiver_account.view_account().await.unwrap().balance;
    assert_eq!(final_receiver_balance.as_yoctonear() - initial_receiver_balance.as_yoctonear(), 1,);

    Ok(())
}
```
