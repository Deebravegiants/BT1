### Title
Missing deposit refund on external registrar-call failure in `address_check_callback` - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The `WalletContract::rlp_execute` entry point accepts an attached NEAR deposit from a caller (`caller_deposit`) and forwards it through a chain of promise callbacks that ultimately execute the user's requested action. When the target of a base-token transfer is another eth-implicit account, `rlp_execute` first dispatches a cross-contract call to an external `address_registrar` contract and schedules `address_check_callback` to process the result. If that external call fails, the caller's attached deposit is never refunded, unlike the equivalent failure path in `rlp_execute_callback`, which explicitly returns the deposit to the caller.

### Finding Description
`inner_rlp_execute` computes `caller_deposit` from the attached deposit of an external (non-self) caller [1](#0-0) , and for `EOABaseTokenTransfer` targets requiring an address check, it calls out to an external `address_registrar` contract, chaining the result into `address_check_callback` while carrying `caller_deposit` as a parameter [2](#0-1) .

Inside `address_check_callback`, when the registrar lookup fails (`PromiseResult::Failed`), the function immediately returns an `ExecuteResponse` marking the transaction as failed, without ever creating a refund promise for `caller_deposit`: [3](#0-2) 

This is inconsistent with the sibling callback `rlp_execute_callback`, which handles the exact same class of failure (`PromiseResult::Failed` from a downstream cross-contract call) by explicitly creating a transfer promise back to the caller before returning the failed response: [4](#0-3) 

The `caller_deposit` parameter passed into `address_check_callback` is only consumed in the success branch (forwarded further down the promise chain to `rlp_execute_callback`) [5](#0-4) ; it is silently dropped on the `PromiseResult::Failed` path, so the attached NEAR is retained by the wallet contract with no code path that returns it to the original caller.

This mirrors the reported bug class in `ExchangeStargateV2Adapter::lzCompose()`: an external dependency call in the middle of a multi-step cross-contract flow can fail (there, `IExchange.deposit()`; here, the `address_registrar.lookup()` call), and the surrounding code lacks the equivalent of a "catch" branch to return funds to the rightful owner, resulting in funds being stuck in the contract.

### Impact Explanation
Any external caller who attaches a deposit while relaying an Ethereum-emulated base-token transfer to another eth-implicit account, where the address registrar is unavailable, buggy, redeployed to be incompatible, or otherwise fails the cross-contract call, will have their attached NEAR deposit permanently retained by the `WalletContract` instance instead of refunded. Unlike a validator/network-level issue, this is directly reachable from an ordinary NEAR transaction submitted by an unprivileged account calling `rlp_execute`, and results in unauthorized retention (loss) of the caller's funds — a "temporary/permanent freezing of user funds" class impact, matching the accepted impact categories.

### Likelihood Explanation
This requires the `address_registrar.lookup` cross-contract call to fail while `address_check_callback` is invoked, which happens whenever an `EOABaseTokenTransfer` has `address_check: Some(_)` set (i.e., transfers targeting another eth-implicit account) [6](#0-5) . Such failures can occur due to insufficient prepaid gas (`REGISTRAR_LOOKUP_GAS` is a fixed constant, `Gas::from_tgas(5)`) [7](#0-6) , the registrar contract being paused/upgraded incompatibly, or account/state issues on the registrar side — none of which require a malicious or privileged actor, only ordinary external conditions affecting a dependency contract. Given the wallet contract only allows one in-flight transaction at a time, an external attacker or griefer could also intentionally engineer registrar failures (e.g., via gas exhaustion) to strand deposits repeatedly.

### Recommendation
In `address_check_callback`, mirror the refund logic already used in `rlp_execute_callback`: on `PromiseResult::Failed`, if `caller_deposit` is `Some`, create a refund promise via `env::promise_batch_create` and `env::promise_batch_action_transfer` to return the deposit to `caller_deposit.account_id` before returning the failure `ExecuteResponse`, exactly as done at [8](#0-7) .

### Proof of Concept
Conceptual PoC (analogous to the reported Solidity PoC):
1. An external (non-self) caller invokes `rlp_execute` with a signed transaction that is an `EOABaseTokenTransfer` whose `target` is another eth-implicit account (triggering `address_check: Some(address)`), attaching a NEAR deposit as `caller_deposit`.
2. `inner_rlp_execute` schedules a call to `address_registrar.lookup(address)` chained to `address_check_callback`, carrying `caller_deposit` [9](#0-8) .
3. Cause the registrar call to fail (e.g., insufficient `REGISTRAR_LOOKUP_GAS`, registrar contract unavailable/panicking).
4. `address_check_callback` observes `PromiseResult::Failed` and returns `ExecuteResponse{success: false, ...}` without issuing any refund transfer [10](#0-9) .
5. Compare against the existing test `test_caller_refunds`, which verifies refunds occur when `rlp_execute_callback` observes a failed downstream promise [11](#0-10)  — no equivalent test or refund exists for the `address_check_callback` failure path, confirming the gap (verified via search finding no test named/covering `address_check_callback` failure in `sanity.rs`).

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L36-36)
```rust
const REGISTRAR_LOOKUP_GAS: Gas = Gas::from_tgas(5);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L140-148)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L174-189)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs (L197-213)
```rust
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
