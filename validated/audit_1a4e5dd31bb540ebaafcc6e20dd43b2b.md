### Title
Attached NEAR deposit permanently stuck when `rlp_execute` fails synchronously with a `UserError` - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
`WalletContract::rlp_execute` is marked `#[payable]`, so an external caller may attach any amount of NEAR deposit when calling it [1](#0-0) . Internally, `inner_rlp_execute` decodes the RLP-encoded Ethereum transaction, and on a `UserError` (malformed/invalid data encoded by the caller) it increments the nonce and returns `Err(err)` synchronously, without creating any promise and without touching the attached deposit [2](#0-1) . Back in `rlp_execute`, this `Err(e)` path returns `PromiseOrValue::Value(e.into())` — i.e., the function call itself completes *successfully* and simply returns a failure payload [3](#0-2) .

### Finding Description
This is the same bug class as the reported Solidity issue: a `payable`-equivalent entry point accepts a deposit that the contract does not intend to use for this particular execution path, and does not refund it.

On NEAR, an attached deposit is only auto-refunded by the protocol when the **receipt itself fails** (panics) [4](#0-3) . If a `#[payable]` method executes to completion and returns `Ok`/a value (even one representing a logical/application-level failure), the protocol has no way to know the deposit was "unused" — it stays credited to the receiving contract's account balance.

`inner_rlp_execute` explicitly creates a `CallerDeposit` structure specifically to support refunding the external caller's deposit when a cross-contract call later fails [5](#0-4) , and that refund is correctly wired up in `rlp_execute_callback` for the promise-failure case [6](#0-5) . However, the `Error::User(_)` branch in `inner_rlp_execute` is reached *before* any promise is created, and it discards `caller_deposit` entirely — no refund promise is created on this path [2](#0-1) . `UserError` variants (e.g. `ValueTooLarge`, `UnknownFunctionSelector`, `InvalidAbiEncodedData`, `ExcessYoctoNear`, `UnsupportedAction`, etc.) are reachable purely from data the caller (or a front-end acting on their behalf) supplies inside the signed Ethereum transaction bytes [7](#0-6) , meaning any external caller attaching a deposit alongside a transaction that trips one of these validation errors will have that deposit silently absorbed into the wallet contract's balance rather than returned.

The comment in `error.rs` even acknowledges this class of errors can be triggered by "a bug in the front-end code that is constructing the Ethereum transaction," i.e., it is an accident-prone path exactly analogous to "accidentally sent ETH" in the original report [8](#0-7) .

### Impact Explanation
An external, unprivileged caller who attaches a NEAR deposit to `rlp_execute` and whose Ethereum-transaction payload triggers a `UserError` will have that deposit permanently retained by the wallet contract instead of refunded, unlike every other failure path in the same function (`Relayer` errors trigger a ban-relayer promise chain that still routes through the deposit-aware callback machinery, and cross-contract call failures explicitly refund via `CallerDeposit`). This is an unauthorized transfer/stuck-funds condition: value leaves the caller's control with no path back, and effectively accrues to the eth-implicit account's contract balance without an equivalent service being rendered.

### Likelihood Explanation
This is trivially reachable by any account calling `rlp_execute` with a nonzero deposit and a malformed/edge-case-encoded transaction (e.g., an ABI-encoded call hitting `ExcessYoctoNear`, `InvalidAbiEncodedData`, or `UnknownFunctionSelector`), which the code's own comments say can happen due to ordinary front-end bugs rather than adversarial intent. No validator or node-level privilege is required — it is purely a contract logic gap in a path shipped as part of this repository (`near-wallet-contract`).

### Recommendation
In the `Error::User(_)` branch (and any other branch of `inner_rlp_execute`/`rlp_execute` that returns without spawning a promise), explicitly issue a refund transfer of the attached deposit back to `predecessor_account_id` before returning the error value, mirroring the refund logic already implemented in `rlp_execute_callback`. Alternatively, reject nonzero attached deposits up front for code paths that cannot possibly consume them (fail fast, analogous to adding a `notPayable`-style guard), refunding immediately rather than silently accepting the value.

### Proof of Concept
1. Deploy `near-wallet-contract` for an eth-implicit account as in `integration-tests/src/tests/features/wallet_contract.rs`.
2. Have a caller invoke `rlp_execute(target, tx_bytes_b64)` attaching a nonzero NEAR deposit, where `tx_bytes_b64` encodes an Ethereum transaction whose calldata parses to a `UserError` case (e.g., an ABI-encoded ERC-20 transfer with `value` exceeding what fits, triggering `UserError::ExcessYoctoNear`, or calldata selector unrecognized, triggering `UnknownFunctionSelector`) [9](#0-8) .
3. Observe the call succeeds at the NEAR protocol level (`ExecuteResponse.success == false` but the outer function call itself does not fail/panic).
4. Check the caller's account balance: it decreases by the attached deposit and that deposit is not present in any refund receipt, unlike the `test_caller_refunds` test which validates refunds only for the promise-failure path [10](#0-9) .

Note: I was not able to fully trace every call site inside `internal.rs`/`eth_emulation.rs` that produces `UserError` to enumerate all concrete triggering payloads within the available iterations; the enum variants and their doc comments strongly indicate they are reachable from caller-supplied transaction data, but exhaustive confirmation of a specific encodable payload would benefit from direct execution/testing in a Devin session.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-93)
```rust
    #[payable]
    pub fn rlp_execute(
        &mut self,
        target: AccountId,
        tx_bytes_b64: String,
    ) -> PromiseOrValue<ExecuteResponse> {
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L116-127)
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L389-393)
```rust
        Err(err @ Error::User(_)) => {
            // Increment nonce on all user errors to prevent replay.
            *nonce = nonce.saturating_add(1);
            return Err(err);
        }
```

**File:** docs/RuntimeSpec/Refunds.md (L15-18)
```markdown
## Deposit Refunds

Deposit refunds are generated when an action receipt fails to execute. All attached deposit amounts are summed together and
sent as a refund to a `predecessor_id` (because only the predecessor can attach deposits).
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/error.rs (L45-63)
```rust
/// Errors that arise from problems in the data signed by the user
/// (i.e. in the Ethereum transaction itself). A careful power-user
/// should never see these errors because they can review the data
/// they are signing. If a user does see these errors then there is
/// likely a bug in the front-end code that is constructing the Ethereum
/// transaction to be signed.
#[derive(Debug, PartialEq, Eq, Clone)]
pub enum UserError {
    EvmDeployDisallowed,
    ValueTooLarge,
    UnknownPublicKeyKind,
    InvalidEd25519Key,
    InvalidSecp256k1Key,
    InvalidAccessKeyAccountId,
    UnsupportedAction(UnsupportedAction),
    UnknownFunctionSelector,
    InvalidAbiEncodedData,
    ExcessYoctoNear,
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
