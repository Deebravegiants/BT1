## Finding: hardcoded gas constants in Wallet Contract callback chain can permanently brick `rlp_execute`

### Title
Hardcoded static gas constants in the ETH Wallet Contract callback chain can become insufficient after future gas-cost repricing, causing a permanent DoS - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The Solidity `transfer()` bug class ("depends on gas consts") is about a caller hard-coding a gas amount for a callback/fallback that may become insufficient if future gas-cost changes make the same logic more expensive, breaking the recipient's execution. The NEAR Wallet Contract (`runtime/near-wallet-contract/implementation/wallet-contract`, the ETH-transaction-emulation contract deployed on eth-implicit accounts) has a direct structural analog: it hard-codes fixed `Gas::from_tgas(5)` constants for its own promise callbacks rather than deriving them from measured/estimated costs, and it relies on one of those callbacks executing to completion to reset a critical liveness flag.

### Finding Description
`WalletContract` defines several fixed gas budgets for its callback chain: [1](#0-0) 

These constants are used as `with_static_gas(...)` amounts for `rlp_execute_callback`, `address_check_callback`, and `nep_141_storage_balance_callback`: [2](#0-1) 

The entry point `rlp_execute` guards against concurrent execution using `has_in_flight_tx`, which is only reset to `false` at the very start of the terminal callback (`rlp_execute_callback`, `address_check_callback`, `nep_141_storage_balance_callback`): [3](#0-2) [4](#0-3) 

If the fixed 5 Tgas budget attached to one of these callbacks ever becomes insufficient for the callback's own logic (e.g. a future NEAR protocol runtime-config update repricing `action_function_call`, `action_transfer`, `new_action_receipt`, or WASM host costs upward, as has previously happened between the `parameters.yaml`/`parameters_testnet.yaml` snapshots seen in `core/parameters/res/runtime_configs/`), the callback receipt will exceed prepaid gas and panic. Because NEAR contract state changes are only committed if the function call completes without panicking, the very first statement of the callback (`self.has_in_flight_tx = false;`) would be rolled back along with everything else, permanently leaving `has_in_flight_tx == true`. From then on, every call to `rlp_execute` is rejected: [5](#0-4) 

There is no other code path that resets `has_in_flight_tx`, so the contract account becomes permanently unable to process any further Ethereum-style transactions.

### Impact Explanation
This is a real, protocol-adjacent impact category ("chain stall"/DoS at the account level, akin to unauthorized state lock): a legitimate user's ETH-compatible NEAR account (deployed with the Wallet Contract) can become permanently bricked with respect to its primary `rlp_execute` entry point if future gas-cost changes push the actual cost of the callback logic above the hard-coded 5 Tgas constants. Given the contract already has a test asserting that an under-provisioned `rlp_execute` call cleanly fails and leaves the contract usable (`test_insufficient_gas` in `sanity.rs`), the developers evidently did not consider the equivalent failure occurring *inside* the internally-fixed callback gas budgets, where failure is unrecoverable rather than a clean error.

### Likelihood Explanation
Likelihood is contingent on an external factor — future NEAR protocol gas repricing (via `RuntimeConfig`/`ActionCosts` changes) — similar to the original ENS finding depending on future EVM opcode repricing. The nearcore repo history shows gas costs for actions and host functions are periodically re-estimated and changed (as seen across `parameters.yaml`, `parameters_testnet.yaml`, and multiple protocol-version snapshots), so this is a plausible, recurring event rather than a purely hypothetical one. The 5 Tgas margins here are also comparatively tight relative to the multiple nested cross-contract calls involved (registrar lookup, storage_balance_of, storage_deposit, ft_transfer, callback), giving less headroom than a single simple operation.

### Recommendation
- Do not hard-code fixed `Gas::from_tgas(5)` budgets for callback logic; instead measure/estimate the actual cost of each callback (similar to how core protocol action costs are estimated in `runtime/runtime-params-estimator`) and add a safety margin, or use `promise_batch_action_function_call_weight` / unspent-gas-weight forwarding so the callback receives a scaled share of remaining gas rather than a fixed absolute amount.
- Ensure `has_in_flight_tx` can be recovered even if a callback panics — e.g. by resetting it in a wrapping receipt with guaranteed gas, or by adding a privileged/self-only recovery method, so an out-of-gas panic in a callback cannot permanently disable the contract.

### Proof of Concept
1. Deploy `WalletContract` at an eth-implicit account and perform a normal `rlp_execute` (e.g. an ERC20 transfer path that ends up in `nep_141_storage_balance_callback` then `rlp_execute_callback`).
2. Simulate (or wait for) a NEAR protocol runtime-config upgrade that increases the gas cost of the operations performed inside `rlp_execute_callback`/`nep_141_storage_balance_callback` (e.g. `action_transfer`, `new_action_receipt`, or relevant WASM host costs) such that the logic no longer fits in the hard-coded `RLP_EXECUTE_CALLBACK_GAS`/`NEP_141_STORAGE_BALANCE_CALLBACK_GAS` budgets.
3. Call `rlp_execute` again; the dispatched callback receipt exceeds its statically attached gas and fails with `GasExceeded`.
4. Because the callback's `self.has_in_flight_tx = false;` write is rolled back along with the rest of the failed receipt, `has_in_flight_tx` remains `true`.
5. All subsequent calls to `rlp_execute` are now rejected at the check in [5](#0-4) , permanently bricking the account's Ethereum-transaction-emulation entry point.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L34-41)
```rust
const NEP_141_STORAGE_DEPOSIT_GAS: Gas = Gas::from_tgas(5);
const NEP_141_STORAGE_BALANCE_OF_GAS: Gas = Gas::from_tgas(5);
const REGISTRAR_LOOKUP_GAS: Gas = Gas::from_tgas(5);
const RLP_EXECUTE_CALLBACK_GAS: Gas = Gas::from_tgas(5);
const ADDRESS_CHECK_CALLBACK_GAS: Gas = Gas::from_tgas(5).saturating_add(RLP_EXECUTE_CALLBACK_GAS);
const NEP_141_STORAGE_BALANCE_CALLBACK_GAS: Gas = Gas::from_tgas(5)
    .saturating_add(NEP_141_STORAGE_DEPOSIT_GAS)
    .saturating_add(RLP_EXECUTE_CALLBACK_GAS);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L89-128)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L276-294)
```rust
    pub fn rlp_execute_callback(
        &mut self,
        caller_deposit: Option<CallerDeposit>,
    ) -> ExecuteResponse {
        self.has_in_flight_tx = false;
        let n = env::promise_results_count();

        if n == 0 {
            // `rlp_execute_callback` is called directly in the case of an emulated self-transfer.
            return ExecuteResponse { success: true, success_value: None, error: None };
        } else if n > 1 {
            return ExecuteResponse {
                success: false,
                success_value: None,
                error: Some(format!(
                    "Invariant violation: this callback comes after a single promise. n={n}"
                )),
            };
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L412-472)
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
    };
    Ok(promise)
```
