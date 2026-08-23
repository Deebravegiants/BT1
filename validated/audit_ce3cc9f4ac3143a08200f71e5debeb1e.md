### Title
Unrecoverable "force-pause" of `WalletContract` via gas-griefing in async callback causes permanent `has_in_flight_tx` lock - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The NEAR `WalletContract` (the ETH-emulation account-abstraction contract deployed for eth-implicit accounts) uses a boolean guard `has_in_flight_tx` to serialize transaction processing, exactly like the Auction contract's `paused` flag serializes bidding. The guard is only ever cleared inside async callback methods, and NEAR's receipt execution model discards *all* state writes of a receipt (including earlier successful writes) when that receipt later aborts (e.g. due to running out of its fixed prepaid gas). An external, attacker-controlled contract invoked from the promise chain can return an oversized response that makes the callback exceed its statically-sized gas budget, aborting the receipt and reverting the flag reset. This leaves `has_in_flight_tx` stuck at `true` forever, permanently "pausing" the wallet contract with no unpause mechanism — a stronger analog of the reported Auction bug, since here the DoS is irrecoverable rather than DAO-unpauseable.

### Finding Description
`WalletContract::rlp_execute` refuses to process any new transaction while `has_in_flight_tx == true`: [1](#0-0) 

The flag is set to `true` right before returning a `Promise` chain, and is only reset to `false` as the *first* statement inside the various `#[private]` callbacks (`address_check_callback`, `nep_141_storage_balance_callback`, `rlp_execute_callback`): [2](#0-1) [3](#0-2) [4](#0-3) 

For the emulated ERC-20 transfer flow, the contract calls `storage_balance_of` on the (attacker-influenceable) `token_id` account with a small, fixed static gas budget, and later deserializes the response in the callback with its own separate fixed gas budget plus the user's declared `action.gas()`: [5](#0-4) [6](#0-5) 

Note the code even documents that "malicious token contracts" are an anticipated adversary for this design: [7](#0-6) 

NEAR's runtime commits or discards a receipt's entire set of trie writes atomically — if any action within a receipt aborts, all state changes made earlier in that same receipt (even ones already executed) are rolled back, as verified by the test: [8](#0-7) 

Putting these together: if the token contract returns an oversized/expensive-to-parse `Successful` payload from `storage_balance_of`, `serde_json::from_slice::<Option<StorageBalance>>(&value)` inside `nep_141_storage_balance_callback` can consume more gas than the callback's fixed prepaid budget, causing the whole callback receipt to abort with `HostError::GasExceeded`/`GasLimitExceeded`. Because the receipt aborts, the `self.has_in_flight_tx = false;` write executed at the top of the same function is discarded together with the rest of the receipt's state changes, leaving `has_in_flight_tx` permanently `true`. There is no code path anywhere in the contract that can reset it afterward (unlike the Auction contract's DAO-controlled `unpause()`), so `rlp_execute` will reject every future transaction for that account forever.

### Impact Explanation
This is an unauthorized, irrecoverable state corruption of a protocol-level account-abstraction contract shipped with nearcore: an unprivileged party (any account that deploys an ordinary NEP-141-style contract and is targeted, even indirectly via a normal signed transfer transaction) can permanently brick another user's `WalletContract`, disabling all further ETH-emulated transaction execution for that account with no recovery path in-protocol. This is materially worse than the referenced Auction finding, which was rated Medium specifically because the DAO could cheaply unpause; here there is no unpause at all.

### Likelihood Explanation
The precondition (a user/relayer submitting a validly RLP-signed ERC-20-style transfer whose `to` target resolves to an attacker-controlled "token" contract) is a realistic, low-cost, purely off-chain-attacker scenario — identical in spirit to a "malicious/rug ERC-20 token" in the Ethereum ecosystem, which the code's own comments acknowledge as an expected threat. No validator or node privilege is required, and the gas budgets involved (`NEP_141_STORAGE_BALANCE_OF_GAS` / `NEP_141_STORAGE_BALANCE_CALLBACK_GAS`) are small, fixed constants that a deliberately oversized JSON response can straightforwardly exceed.

### Recommendation
- Move the `has_in_flight_tx = false` reset (and any other invariant-critical writes) so it does not depend on the remainder of the callback succeeding — e.g. reset the flag via a dedicated, minimal-gas guaranteed step, or use a `#[callback_unwrap]`/panic-safe pattern that still commits the reset even when later logic runs out of gas.
- Bound/validate the size of cross-contract call results before deserializing them (reject or truncate implausibly large `PromiseResult::Successful` payloads) instead of unconditionally calling `serde_json::from_slice` on attacker-controlled bytes.
- Add an explicit, permissioned or time-based recovery path to clear `has_in_flight_tx` if a promise chain never resolves it, so a single gas-griefed callback cannot permanently disable the account.

### Proof of Concept
1. Attacker deploys a NEAR contract at account `evil.token` implementing `storage_balance_of` to always return a very large JSON byte blob (sized just under the return-value length limit) instead of `null`/a small struct.
2. Victim (or a relayer on their behalf) submits to their `WalletContract` an RLP-encoded ETH transaction emulating an ERC-20 transfer with `to` = `evil.token`, calling `rlp_execute(target=evil.token, tx_bytes_b64=...)`.
3. `inner_rlp_execute` sets `has_in_flight_tx = true` and creates `Promise::new(evil.token).function_call("storage_balance_of", ...)` with `NEP_141_STORAGE_BALANCE_OF_GAS` (5 TGas), chained `.then()` to `nep_141_storage_balance_callback` with its own fixed gas budget.
4. `evil.token::storage_balance_of` succeeds (well within 5 TGas) but its return value is the oversized blob.
5. `nep_141_storage_balance_callback` executes: sets `has_in_flight_tx = false`, then calls `serde_json::from_slice(&value)` on the oversized blob at line 211, which burns more gas than the callback's fixed prepaid amount and aborts with `GasExceeded`/`GasLimitExceeded`.
6. Because the whole receipt aborts, the runtime discards all of its state writes (per the rollback semantics referenced above), so `has_in_flight_tx` reverts back to `true` in the persisted trie state.
7. Any subsequent call to `rlp_execute` on this account now immediately returns the "transaction already in progress" error forever, since nothing can ever set `has_in_flight_tx` back to `false`.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L28-33)
```rust
/// This storage deposit value is the one used by the standard NEP-141 implementation,
/// which essentially all tokens use. Therefore we hard-code it here instead of doing
/// the extra on-chain call to `storage_balance_bounds`. This also prevents malicious
/// token contracts with very high `storage_balance_bounds` from taking lots of $NEAR
/// from eth-wallet-contract users.
const NEP_141_STORAGE_DEPOSIT_AMOUNT: NearToken = NearToken::from_yoctonear(1_250 * MICRO_NEAR);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L97-105)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L139-148)
```rust
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L201-221)
```rust
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L439-458)
```rust
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
```

**File:** test-loop-tests/src/tests/yield_resume.rs (L351-394)
```rust
/// Similar to `test_yield_then_resume_two_actions`, but after the first action, another action fails.
/// When processing the receipt fails, the yielded receipt should be cancelled and there should be
/// no PromiseYieldStatus in the state, even though it was written by the first action.
#[test]
fn test_yield_then_resume_two_actions_failure() {
    let mut env = prepare_env();
    let signer = create_user_test_signer(&AccountId::from_str("test0").unwrap());
    let genesis_block = env.validator().client().chain.get_block_by_height(0).unwrap();
    let yield_payload = vec![6u8; 16];

    let tx = SignedTransaction::from_actions(
        200,
        "test0".parse().unwrap(),
        "test0".parse().unwrap(),
        &signer,
        vec![
            Action::FunctionCall(Box::new(FunctionCallAction {
                method_name: "call_yield_create_return_promise".to_string(),
                args: yield_payload.clone(),
                gas: Gas::from_teragas(100),
                deposit: Balance::ZERO,
            })),
            Action::FunctionCall(Box::new(FunctionCallAction {
                method_name: "panic_with_message".to_string(),
                args: Vec::new(),
                gas: Gas::from_teragas(50),
                deposit: Balance::ZERO,
            })),
            Action::FunctionCall(Box::new(FunctionCallAction {
                method_name: "call_yield_resume_read_data_id_from_storage".to_string(),
                args: yield_payload,
                gas: Gas::from_teragas(100),
                deposit: Balance::ZERO,
            })),
        ],
        *genesis_block.hash(),
    );

    let res = env.validator_runner().execute_tx(tx, Duration::seconds(5));
    assert_matches!(res.unwrap().status, FinalExecutionStatus::Failure(_));

    // PromiseYieldStatus change was not committed to the trie.
    assert_no_promise_yield_status_in_state(&env);
}
```
