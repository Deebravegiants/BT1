This confirms the analog. The `#[payable] rlp_execute` method in the near-wallet-contract early-returns without ever consuming or refunding the attached deposit when a transaction is already in flight.### Title
`WalletContract::rlp_execute` swallows attached deposit when a transaction is already in flight - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
`rlp_execute` is the payable entry point of the `near-wallet-contract` (the on-chain contract that lets an Ethereum-style EOA control a NEAR account). It checks `self.has_in_flight_tx` before doing anything else and, if true, returns a failure value without ever inspecting or handling `env::attached_deposit()`. Because NEAR credits an attached deposit to the receiving account's balance before contract logic executes, any yoctoNEAR sent with this rejected call is retained by the wallet contract forever, with no refund path and no record kept of who sent it. This mirrors the reported `RewardsDistributor.claim()` bug: an early-return branch is reached with a positive "value" attached, and that value is neither validated nor refunded, ultimately being silently absorbed by the contract.

### Finding Description
`rlp_execute` is declared `#[payable]`, so callers may (and, per its own design for emulated ETH transactions, are expected to) attach a deposit: [1](#0-0) 

The very first check in the method is the in-flight-transaction guard, which returns `PromiseOrValue::Value(...)` immediately, before `env::attached_deposit()` is ever read:

```rust
#[payable]
pub fn rlp_execute(...) -> PromiseOrValue<ExecuteResponse> {
    if self.has_in_flight_tx {
        return PromiseOrValue::Value(ExecuteResponse {
            success: false, success_value: None,
            error: Some("Error: transaction already in progress, please try again later.".into()),
        });
    }
    ...
}
``` [2](#0-1) 

Only in the non-early-return path does the contract construct an `ExecutionContext` from `env::attached_deposit()` and build a `CallerDeposit` to track it for a possible refund: [3](#0-2) 

The refund mechanism itself only fires from `rlp_execute_callback` on `PromiseResult::Failed`, using the `CallerDeposit` that was captured on the *successful* path: [4](#0-3) [5](#0-4) 

Because NEAR's runtime semantics credit `attached_deposit` to the receiving account's balance immediately, before any contract code runs (as documented in the Economics API spec: "`attached_deposit` -- the balance that was attached to the call that will be immediately deposited before the contract execution starts"), any deposit sent alongside a call that hits the `has_in_flight_tx` early-return is already part of the wallet contract's balance by the time the guard clause runs, and no code path ever issues a transfer back to the caller for it: [6](#0-5) 

There is a documented invariant about `has_in_flight_tx`, but it only concerns promise-bookkeeping ordering, not deposit accounting: [7](#0-6) 

The existing test suite exercises `has_in_flight_tx` rejection only for a batch of two `rlp_execute` calls in the same NEAR transaction, and neither call in that test attaches a deposit, so the loss is not observed: [8](#0-7) 

The correctly-handled deposit-refund case only covers "cross-contract call fails," i.e. it starts from the assumption that `caller_deposit` was already computed inside `inner_rlp_execute` — the in-flight guard bypasses that entirely: [9](#0-8) 

### Impact Explanation
Users interacting with the wallet contract via an Ethereum-style relayed transaction that carries native-token value (e.g. an emulated base-token transfer or ERC-20 transfer with a relayer fee, which is exactly the flow that attaches a deposit through `Wei` → yoctoNEAR conversion, see the `create_rlp_execute_tx` helper) are exposed: if a relayer submits such a transaction while a prior transaction from the same wallet is still in flight (a race condition that is entirely plausible for asynchronous relayers, competing relayers, or retried submissions), the attached value is permanently absorbed into the wallet contract's balance. This is a "permanent freezing/loss of funds" for the depositor — the deposit is not returned, not applied to the intended action, and there is no accounting (`CallerDeposit`) created for it since the early return happens before `CallerDeposit::new` is ever called. It matches the "impact: permanent freezing of funds" class from the reference report exactly, translated to NEAR's `attached_deposit` model.

### Likelihood Explanation
Likelihood is low-to-medium, similar to the original report: it requires the "transaction already in progress" branch to be hit — i.e., a second `rlp_execute` call must land on the wallet account while an earlier one's asynchronous promise chain is still unresolved, and that second call must have a non-zero deposit attached. This is realistic for the ETH-emulation use case (relayers submitting user-signed Ethereum transactions with value), especially under retries, competing relayers, or network delays, but it is not the default single-happy-path flow, hence "medium" rather than "high" likelihood.

### Recommendation
In `rlp_execute` (and any other public payable entry point reachable while `has_in_flight_tx` is true), read `env::attached_deposit()` before the early-return check and, if it is non-zero, either (a) reject the call outright when a deposit is attached and a transaction is already in flight, or (b) issue an immediate refund transfer to `env::predecessor_account_id()` as part of the failure response, mirroring the existing `rlp_execute_callback` refund logic. This closes the gap symmetrically with the "recommendation" in the original report (validate/handle the attached value on every early-return branch, not just the main success path).

### Proof of Concept
No PoC was executed (this is a static, read-only code review); the vulnerable path can be exercised conceptually as follows:
1. Deploy `WalletContract` and note its `eth_implicit_account`.
2. Submit a batch transaction similar to `test_simultaneous_transactions` (see `runtime/near-wallet-contract/implementation/wallet-contract/src/tests/sanity.rs:121-168`), but attach a non-zero deposit to the **second** `rlp_execute` call in the batch (or send it via a separate NEAR transaction that lands while `has_in_flight_tx` is still `true` from the first call).
3. Observe that the second call returns `ExecuteResponse { success: false, error: Some("Error: transaction already in progress...") }`.
4. Query the wallet contract account balance before/after: the attached deposit from step 2 is retained in the wallet's balance permanently — no refund receipt is ever generated, unlike the `test_caller_refunds` scenario which only refunds deposits that made it past the `has_in_flight_tx` check. [8](#0-7)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L48-54)
```rust
    /// Tracks whether a transaction is currently being executed
    /// (i.e. has receipts that have not yet resolved).
    /// Invariant: `has_in_flight_tx` must be `true` when a mutable method
    /// of this contract returns a promise and `false` otherwise (except
    /// for the check if a transaction is already in flight at the beginning
    /// of `rlp_execute`).
    pub has_in_flight_tx: bool,
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-105)
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
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-317)
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
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L330-345)
```rust
fn inner_rlp_execute(
    current_account_id: AccountId,
    predecessor_account_id: AccountId,
    target: AccountId,
    tx_bytes_b64: String,
    nonce: &mut u64,
) -> Result<Promise, Error> {
    if *nonce == u64::MAX {
        return Err(Error::AccountNonceExhausted);
    }
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

**File:** docs/RuntimeSpec/Components/BindingsSpec/EconomicsAPI.md (L7-15)
```markdown
- `account_balance` -- the balance attached to the given account. This includes the `attached_deposit` that was attached
  to the transaction;
- `attached_deposit` -- the balance that was attached to the call that will be immediately deposited before
  the contract execution starts;
- `prepaid_gas` -- the tokens attached to the call that can be used to pay for the gas;
- `used_gas` -- the gas that was already burnt during the contract execution and attached to promises (cannot exceed `prepaid_gas`);

If contract execution fails `prepaid_gas - used_gas` is refunded back to `signer_account_id` and `attached_deposit`
is refunded back to `predecessor_account_id`.
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
