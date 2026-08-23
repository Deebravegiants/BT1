## Title
External caller's attached deposit is permanently trapped (not refunded) on several early-return error paths in `WalletContract` cross-contract callbacks - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The `near-wallet-contract` (the eth-implicit account wallet contract shipped with nearcore) accepts a `#[payable]` deposit from an external caller in `rlp_execute()` and is designed to always refund that deposit to the caller if the resulting cross-contract action ultimately fails. This refund logic is implemented via the `CallerDeposit` struct, which is threaded through the promise chain and consulted in `rlp_execute_callback()` when `PromiseResult::Failed` is observed. However, two intermediate callbacks in the same promise chain — `address_check_callback` and `nep_141_storage_balance_callback` — have multiple early-return branches that discard the `caller_deposit` parameter without issuing any refund transfer, permanently stranding the caller's attached NEAR in the wallet contract's balance. This mirrors the reported Solidity bug class: a payment-refund mechanism exists in the codebase, but specific failure/edge-case branches silently drop the value instead of returning it, resulting in loss of the caller's funds.

### Finding Description
`rlp_execute()` is `#[payable]` and captures the caller's `attached_deposit` into a `CallerDeposit` (tracked only for external, non-self callers): [1](#0-0) 

This `caller_deposit` is threaded through to `address_check_callback` when the target is another eth-implicit account requiring a registrar lookup: [2](#0-1) 

Inside `address_check_callback`, three distinct failure branches return an `ExecuteResponse` error directly, discarding `caller_deposit` without ever creating a refund promise:
- when the registrar lookup promise itself fails (`PromiseResult::Failed`)
- when the registrar response cannot be deserialized
- when the target resolves to an existing named account and the caller is not using an access key (`env::signer_account_id() != current_account_id`) [3](#0-2) 

The same pattern repeats in `nep_141_storage_balance_callback`, used for emulated ERC-20 transfers: both the `PromiseResult::Failed` branch and the JSON-deserialization-failure branch return an error `ExecuteResponse` without refunding `caller_deposit`: [4](#0-3) 

By contrast, the only place a refund is actually issued is in `rlp_execute_callback`, on the final `PromiseResult::Failed` case of the *last* promise in the chain: [5](#0-4) 

This is confirmed by the existing test `test_caller_refunds`, which only exercises the refund path for a failure that reaches `rlp_execute_callback`, not the intermediate callbacks: [6](#0-5) 

Because NEAR credits an attached deposit to the receiving contract's balance as soon as the `#[payable]` receipt executes (regardless of what the function subsequently returns, so long as it doesn't panic), any external caller's deposit that flows through `rlp_execute` → `address_check_callback` or `rlp_execute` → `nep_141_storage_balance_callback` and hits one of the early-return branches above is silently retained by the wallet contract forever, exactly like the described Solidity bug where a value that should trigger a revert/refund is instead silently zeroed/dropped.

### Impact Explanation
Any external caller (e.g., a relayer submitting another user's signed Ethereum-style transaction to a `near-wallet-contract`) who attaches NEAR to `rlp_execute()` for a transaction whose target is another eth-implicit account (triggering the registrar-lookup path) or an emulated ERC-20 transfer (triggering the NEP-141 storage-balance path) can have their deposit permanently trapped if the registrar call fails/returns garbage, or if the target turns out to be an existing named account and the relayer isn't using an access key, or if the NEP-141 `storage_balance_of` call fails/returns garbage. This is a direct, concrete loss of user funds (native NEAR) with no way to recover them, matching "concrete token inflation or theft"/"unauthorized state or balance change" impact criteria via loss of the caller's balance.

### Likelihood Explanation
This is triggerable by any unprivileged external account through the normal, documented `rlp_execute` entry point of a production nearcore component (the wallet contract used for eth-implicit/EVM-compatible accounts). The failure conditions (registrar call failing/malformed response, target already being a registered named account, or a token contract's `storage_balance_of` call failing/returning malformed data) are realistic operational conditions, not adversarial edge cases requiring privileged access, making this readily reachable in normal usage/relaying.

### Recommendation
In `address_check_callback` and `nep_141_storage_balance_callback`, every early-return `ExecuteResponse` error branch should first check `caller_deposit` and, if present, create a refund `Promise` transferring the deposit back to `caller_deposit.account_id`, mirroring the logic already present in `rlp_execute_callback`'s `PromiseResult::Failed` branch. Consider factoring this refund-on-error behavior into a shared helper to avoid the same omission recurring in future callback additions.

### Proof of Concept
1. An external relayer (not the wallet's own account, i.e., `predecessor_account_id != current_account_id`) calls `rlp_execute(target, tx_bytes_b64)` with a nonzero attached deposit, where the decoded transaction is an `EOABaseTokenTransfer` whose `target` is another eth-implicit account (`address_check: Some(address)`), per `parse_rlp_tx_to_action`.
2. This creates a promise chain to the `ADDRESS_REGISTRAR_ACCOUNT_ID` contract's `lookup`, followed by `address_check_callback` with `caller_deposit` set from step 1's attached deposit (see `CallerDeposit::new`).
3. Cause the registrar lookup to fail (e.g., registrar contract paused/out of gas) — `PromiseResult::Failed` — or have it resolve to `Some(account_id)` while the relayer is not using an access key (`env::signer_account_id() != current_account_id`, the normal external-caller case).
4. `address_check_callback` returns `PromiseOrValue::Value(ExecuteResponse { success: false, ... })` directly, never constructing a refund promise for `caller_deposit`.
5. Observe that the relayer's attached NEAR deposit remains permanently in the wallet contract's balance; no receipt refunds it to the caller, unlike the `test_caller_refunds` scenario in [6](#0-5)  which only tests the final-callback failure path.

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L133-192)
```rust
    #[private]
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L194-221)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-312)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L412-432)
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
