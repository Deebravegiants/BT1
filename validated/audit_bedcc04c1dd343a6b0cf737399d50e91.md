### Title
`caller_deposit` Not Refunded on Early-Exit Failures in `nep_141_storage_balance_callback` and `address_check_callback` — (`runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

---

### Summary

The Wallet Contract's `rlp_execute` flow correctly tracks an external caller's attached NEAR deposit via `CallerDeposit` and refunds it in `rlp_execute_callback` when the downstream cross-contract call fails. However, two intermediate callbacks — `nep_141_storage_balance_callback` and `address_check_callback` — return early on failure without issuing that refund. Any NEAR attached by an external caller to `rlp_execute` is permanently stranded in the wallet contract when these callbacks fail early.

---

### Finding Description

`inner_rlp_execute` captures the external caller's attached deposit at line 345:

```rust
let caller_deposit = CallerDeposit::new(&context);
```

`CallerDeposit::new` records a non-`None` value whenever the caller is external and `env::attached_deposit() > 0`. [1](#0-0) 

`rlp_execute_callback` correctly handles the refund on failure:

```rust
PromiseResult::Failed => {
    if let Some(CallerDeposit { account_id, yocto_near }) = caller_deposit {
        let refund_promise = env::promise_batch_create(&account_id);
        env::promise_batch_action_transfer(refund_promise, NearToken::from_yoctonear(yocto_near.into()));
    }
    ...
}
``` [2](#0-1) 

**Bug 1 — `nep_141_storage_balance_callback`**: When `storage_balance_of` fails or returns unparseable JSON, the function returns early with an error `ExecuteResponse` but never touches `caller_deposit`:

```rust
PromiseResult::Failed => {
    return PromiseOrValue::Value(ExecuteResponse { success: false, ... });
    // caller_deposit silently dropped
}
``` [3](#0-2) 

The `caller_deposit` is passed into this callback but is never forwarded to `rlp_execute_callback` on these early-exit paths. [4](#0-3) 

**Bug 2 — `address_check_callback`**: The same pattern occurs when the address registrar call fails or returns unexpected data — `caller_deposit` is received as a parameter but is not refunded on the three early-return paths (lines 142–147, 151–157, 168–172): [5](#0-4) 

The only path that correctly propagates `caller_deposit` is the success path that chains into `rlp_execute_callback` (line 182).

---

### Impact Explanation

An external caller (relayer) who attaches NEAR to `rlp_execute` for an ERC-20 transfer (`EthEmulationKind::ERC20Transfer`) or a base-token transfer with address check (`EOABaseTokenTransfer { address_check: Some(_) }`) will permanently lose that deposit if the intermediate call fails. The NEAR remains in the wallet contract's balance, accessible to the wallet owner. The exact corrupted value is the relayer's account balance (decremented) and the wallet contract's account balance (incremented by the stranded deposit).

---

### Likelihood Explanation

The `rlp_execute` function is `#[payable]`, explicitly designed to accept NEAR deposits from external callers. [6](#0-5) 

A malicious wallet owner can deliberately trigger the failure path by signing an ERC-20 transfer transaction targeting a token contract that panics on `storage_balance_of`. If the relayer attaches NEAR (e.g., to cover a storage deposit or as part of a fee arrangement), the wallet owner captures that deposit. The `test_caller_refunds` test confirms that external callers do attach NEAR to `rlp_execute` in practice. [7](#0-6) 

The constraint is that the relayer must attach NEAR; if `attached_deposit == 0`, `CallerDeposit` is `None` and there is nothing to lose. This limits likelihood but does not eliminate it, since the function is payable and the `CallerDeposit` mechanism exists precisely to handle this case.

---

### Recommendation

Mirror the refund logic from `rlp_execute_callback` in every early-return path of `nep_141_storage_balance_callback` and `address_check_callback`. Before returning an error `ExecuteResponse`, emit a transfer promise back to `caller_deposit.account_id` for `caller_deposit.yocto_near` if `caller_deposit` is `Some`:

```rust
if let Some(CallerDeposit { account_id, yocto_near }) = caller_deposit {
    let refund = env::promise_batch_create(&account_id);
    env::promise_batch_action_transfer(refund, NearToken::from_yoctonear(yocto_near.into()));
}
return PromiseOrValue::Value(ExecuteResponse { success: false, ... });
```

Apply this to all three early-exit branches in `address_check_callback` (lines 142–147, 151–157, 168–172) and both early-exit branches in `nep_141_storage_balance_callback` (lines 204–209, 213–219). [8](#0-7) 

---

### Proof of Concept

1. Deploy a malicious NEP-141 token contract whose `storage_balance_of` method always panics.
2. Wallet owner signs an ERC-20 transfer Ethereum transaction targeting that malicious token contract.
3. Relayer calls `rlp_execute` with `deposit = 1 NEAR` attached.
4. `inner_rlp_execute` records `caller_deposit = Some(CallerDeposit { account_id: relayer, yocto_near: 1e24 })`.
5. The ERC-20 path schedules `storage_balance_of` → `nep_141_storage_balance_callback`.
6. `storage_balance_of` panics; `nep_141_storage_balance_callback` receives `PromiseResult::Failed` and returns early at line 204–209 without refunding `caller_deposit`.
7. The relayer's 1 NEAR is now part of the wallet contract's balance. The wallet owner can spend it freely via subsequent `rlp_execute` calls (e.g., a self-transfer). [9](#0-8)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L180-191)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-93)
```rust
    #[payable]
    pub fn rlp_execute(
        &mut self,
        target: AccountId,
        tx_bytes_b64: String,
    ) -> PromiseOrValue<ExecuteResponse> {
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L134-192)
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
        };
        self.has_in_flight_tx = true;
        PromiseOrValue::Promise(promise)
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L194-220)
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L170-213)
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
```
