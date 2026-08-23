## Analysis

The reported Solidity issue (fixed 30,000 gas stipend for `to.call{gas: 30000}` in `attemptETHTransfer()`) is a bug class about hardcoded, possibly-insufficient gas allocated to a callback/external call, which can cause it to revert and strand funds or state.

The closest reachable analog in nearcore is not in the core runtime's system-generated refund receipts (those are pure `Transfer` actions that never execute contract code, so they cannot "run out of gas" the way a Solidity `receive()` hook can) [1](#0-0) . Instead, the real analog is in the **eth-wallet contract** (`near-wallet-contract`), which is deployed to unprivileged, ETH-implicit user accounts and is the standard mechanism by which any relayer/unprivileged caller submits an RLP-encoded Ethereum transaction to be executed as a NEAR action.

### Title
Hardcoded Static Gas for Wallet-Contract Callbacks May Be Insufficient, Causing Permanent DoS and Loss of Refunded Deposit - (File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs)

### Summary
`WalletContract::rlp_execute` and its callback chain (`address_check_callback`, `nep_141_storage_balance_callback`, `rlp_execute_callback`) attach a fixed, hardcoded amount of gas (`RLP_EXECUTE_CALLBACK_GAS = 5 Tgas`, and related constants) to the terminal callback that finalizes execution and, on failure, refunds any `caller_deposit` to the relayer [2](#0-1) . This mirrors the reported bug class exactly: a fixed, non-configurable gas budget attached to a call whose actual execution cost is not statically bounded/guaranteed to fit.

### Finding Description
`rlp_execute` sets `has_in_flight_tx = true` before returning a promise chain, and the guard at entry rejects any further calls while that flag is true [3](#0-2) . The flag is only reset back to `false` inside the callback functions (`address_check_callback`, `nep_141_storage_balance_callback`, `rlp_execute_callback`), all of which are executed with only `RLP_EXECUTE_CALLBACK_GAS` (5 Tgas) as their *static* gas component [4](#0-3) [5](#0-4) .

Critically, `rlp_execute_callback` itself performs additional logic on the failure path — creating a new promise batch and a `Transfer` action to refund the caller's deposit — inside the very function that was only allotted the fixed 5 Tgas budget [6](#0-5) .

Per nearcore's action-execution model, if a `FunctionCall` action exhausts its attached/prepaid gas (or panics for any other reason), the entire receipt fails and `state_update.rollback()` discards **all** state changes made during that receipt, including the `has_in_flight_tx = false` reset that occurs at the top of the callback [7](#0-6) . Consequently, if the fixed 5 Tgas ever proves insufficient for the callback's logic (e.g., due to future protocol gas-cost changes, additional refund-branch complexity, or unexpectedly large `caller_deposit`/account-id data), the callback fails, the deposit refund never executes (fund loss/stranding), and `has_in_flight_tx` remains permanently `true` in storage — because that assignment is also rolled back. This permanently locks the wallet contract: `rlp_execute` will forever short-circuit with "transaction already in progress" for that account, since there is no other code path that clears `has_in_flight_tx`.

### Impact Explanation
- **Fund loss/stranding**: the caller-deposit refund logic on the `PromiseResult::Failed` branch never executes if the callback itself runs out of gas, so relayers/users can lose deposited NEAR.
- **Permanent Denial of Service**: `has_in_flight_tx` is only ever cleared inside a callback; if that callback's fixed gas allotment is insufficient, the flag update is rolled back and stays `true` forever, permanently disabling the ETH-emulation wallet account (`rlp_execute` will unconditionally reject all future calls) [8](#0-7) .
- This is reachable by any unprivileged caller who submits an RLP-encoded Ethereum transaction to `rlp_execute` — no validator or privileged role is required.

### Likelihood Explanation
Likelihood depends on whether 5 Tgas is actually sufficient margin for `rlp_execute_callback`'s worst-case logic (promise creation + transfer action + response construction) under all current and future gas-cost/config values. The code comments show the authors were already gas-budget-conscious enough to add fixed components on top of dynamic ones for the intermediate callbacks (`ADDRESS_CHECK_CALLBACK_GAS`, `NEP_141_STORAGE_BALANCE_CALLBACK_GAS`), but the **terminal** `rlp_execute_callback` always uses the bare `RLP_EXECUTE_CALLBACK_GAS` constant regardless of whether it needs to take the refund branch, so any underestimation of that specific path's cost (e.g. via protocol fee changes such as `AccountCostIncrease`/gas repricing) directly triggers the failure mode described above. This requires a protocol/config-level gas-repricing event or an edge case increasing the callback's real cost beyond 5 Tgas — plausible but not trivially triggerable by an attacker without such a change occurring first.

### Recommendation
- Do not hardcode a fixed gas budget for `rlp_execute_callback`; either attach unused/prepaid gas via `GasWeight` (as already done elsewhere, e.g. `create_ban_relayer_promise` using `GasWeight(1)` [9](#0-8) ) or add a generous safety margin above measured worst-case cost.
- Ensure `has_in_flight_tx` can be recovered/cleared through an independent mechanism (e.g., a timeout-based reset or an owner-only "force unlock") so an out-of-gas callback cannot permanently brick the wallet contract.
- Add regression/estimator tests that assert the callback succeeds even in the refund branch at the currently configured gas amount, and re-validate after any protocol gas-cost change.

### Proof of Concept
1. Deploy `WalletContract` to an eth-implicit account.
2. Submit an RLP transaction via `rlp_execute` that goes through a path terminating in `rlp_execute_callback` with a non-null `caller_deposit` and whose inner cross-contract call is made to fail (`PromiseResult::Failed`), forcing the refund branch (`promise_batch_create` + `promise_batch_action_transfer`) to execute.
3. Simulate/force a gas-cost increase for host functions used in that branch (or reduce `RLP_EXECUTE_CALLBACK_GAS`) so that the callback's actual execution cost exceeds 5 Tgas.
4. Observe: the callback fails with an out-of-gas action error; the receipt's state changes (including `has_in_flight_tx = false`) are rolled back per `apply_action_receipt` [7](#0-6) ; subsequent calls to `rlp_execute` on the same account are permanently rejected with "transaction already in progress."

### Citations

**File:** docs/RuntimeSpec/Refunds.md (L10-13)
```markdown
Refund receipts are identified by having `predecessor_id == "system"`. They are also special because they don't cost any gas to generate or execute. As a result, they also do not contribute to the block gas limit.

If the execution of a refund fails, the refund amount is burnt.
The refund receipt is an `ActionReceipt` that consists of a single action `Transfer` with the `deposit` amount of the refund.
```

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L94-105)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L179-192)
```rust
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
        };
        self.has_in_flight_tx = true;
        PromiseOrValue::Promise(promise)
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-311)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L459-465)
```rust
        TransactionKind::EthEmulation(EthEmulationKind::SelfBaseTokenTransfer) => {
            // Base token transfers to self are no-ops on Near, so we do not need to
            // schedule an additional call. We can simply go straight to `rlp_execute_callback`.
            let ext: WalletContractExt =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            ext.rlp_execute_callback(caller_deposit)
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L503-512)
```rust
fn create_ban_relayer_promise(current_account_id: AccountId) -> Promise {
    let pk = env::signer_account_pk();
    Promise::new(current_account_id).delete_key(pk).function_call_weight(
        "ban_relayer".into(),
        Vec::new(),
        NearToken::from_yoctonear(0),
        Gas::from_tgas(1),
        GasWeight(1),
    )
}
```

**File:** protocol-model/spec/runtime-execution.md (L70-70)
```markdown
7. **Commit or rollback**: success commits with `ReceiptProcessing`; failure calls `state_update.rollback()`, discarding all state changes from the receipt (`runtime/runtime/src/lib.rs:961`-`970`).
```
