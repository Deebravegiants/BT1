### Title
Attached NEAR Deposit Silently Locked When `rlp_execute` Returns Early on `has_in_flight_tx` — (`runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

---

### Summary

The `rlp_execute` entry point of the Wallet Contract is marked `#[payable]` and accepts an arbitrary NEAR deposit. When `has_in_flight_tx == true`, the function returns an error value immediately — but it never refunds the caller's attached deposit. Because the function call itself succeeds (it returns a `PromiseOrValue::Value`, not a panic), the NEAR runtime does **not** automatically issue a deposit refund. The attached NEAR is permanently credited to the wallet contract's balance, causing a direct financial loss for the caller.

---

### Finding Description

`rlp_execute` is declared `#[payable]`: [1](#0-0) 

When `has_in_flight_tx` is `true`, the function returns a plain `PromiseOrValue::Value(...)` without touching the deposit: [2](#0-1) 

The `CallerDeposit` mechanism — which is the only place a deposit refund is issued — is only triggered inside `rlp_execute_callback` when the downstream promise **fails**: [3](#0-2) 

When the function returns `PromiseOrValue::Value(...)` (i.e., the early-exit path), no callback is ever scheduled, so `rlp_execute_callback` is never reached and no refund is ever issued.

The `CallerDeposit` struct itself only tracks deposits for external (non-self) callers: [4](#0-3) 

A secondary path with the same root cause exists for `AddKey` and `DeleteKey` actions that **succeed**: `try_into_near_action` silently ignores `additional_value` for those variants, so any NEAR the relayer attached is not forwarded to the action and is not refunded on success: [5](#0-4) 

---

### Impact Explanation

Any external caller (relayer) who attaches a non-zero NEAR deposit to `rlp_execute` while `has_in_flight_tx == true` permanently loses that deposit. The NEAR is credited to the wallet contract's account balance, which the wallet owner controls. The corrupted protocol value is the **caller's NEAR balance**: it is decremented without any corresponding action being executed or any refund being issued.

---

### Likelihood Explanation

Relayers attach NEAR to `rlp_execute` when the Ethereum transaction carries a non-zero `value` field (to forward it as a deposit to the inner action). A wallet owner who wants to steal from a relayer can:

1. Sign an Ethereum transaction with a non-zero `value` encoding any action.
2. Submit a first transaction that keeps `has_in_flight_tx = true` for an extended period (e.g., a cross-contract call to a slow or unresponsive contract).
3. Present the signed Ethereum transaction to a relayer, who calls `rlp_execute` with the equivalent NEAR attached.
4. The function returns the "already in progress" error; the relayer's NEAR is not refunded.

The wallet owner gains the relayer's NEAR. Likelihood is **low-to-medium**: it requires a relayer to attach NEAR during an in-flight window, but the wallet owner controls that window and can engineer the timing.

---

### Recommendation

Add an explicit guard at the top of `rlp_execute` (and at any other early-return path) that rejects non-zero deposits when they cannot be consumed:

```rust
if self.has_in_flight_tx {
    require!(
        env::attached_deposit().is_zero(),
        "rlp_execute: deposit must be zero when a transaction is already in progress"
    );
    return PromiseOrValue::Value(ExecuteResponse { ... });
}
```

Alternatively, explicitly refund `env::attached_deposit()` to `env::predecessor_account_id()` before returning on any early-exit path. The same guard should be applied for `AddKey` and `DeleteKey` action paths where the deposit cannot be forwarded.

---

### Proof of Concept

1. Wallet owner calls a cross-contract function that will not resolve for many blocks, setting `has_in_flight_tx = true`.
2. Wallet owner signs an Ethereum transaction with `value = 5 ETH` (≈ 5 × 10^24 yoctoNEAR) encoding an `AddKey` action and hands it to a relayer.
3. Relayer calls `rlp_execute(target, tx_bytes_b64)` with `5 NEAR` attached.
4. `has_in_flight_tx == true` → function returns `PromiseOrValue::Value(ExecuteResponse { success: false, error: "already in progress" })`.
5. No `rlp_execute_callback` is scheduled; `CallerDeposit` is never consulted.
6. NEAR runtime sees a successful function call (returned a value, did not panic) → no automatic deposit refund.
7. Relayer's account loses 5 NEAR; wallet contract's balance gains 5 NEAR. [6](#0-5)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-89)
```rust
    #[payable]
    pub fn rlp_execute(
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L97-128)
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L262-296)
```rust
            Action::AddKey {
                public_key_kind,
                public_key,
                nonce,
                is_full_access,
                is_limited_allowance,
                allowance,
                receiver_id,
                method_names,
            } => {
                let public_key = construct_public_key(public_key_kind, &public_key)?;
                let access_key = if is_full_access {
                    AccessKey { nonce, permission: AccessKeyPermission::FullAccess }
                } else {
                    let allowance = if is_limited_allowance { Some(allowance) } else { None };
                    AccessKey {
                        nonce,
                        permission: AccessKeyPermission::FunctionCall(FunctionCallPermission {
                            allowance: allowance.map(NearToken::from_yoctonear),
                            receiver_id: receiver_id
                                .parse()
                                .map_err(|_| Error::User(UserError::InvalidAccessKeyAccountId))?,
                            method_names,
                        }),
                    }
                };
                let action = AddKeyAction { public_key, access_key };
                near_action::Action::AddKey(action)
            }
            Action::DeleteKey { public_key_kind, public_key } => {
                let action = DeleteKeyAction {
                    public_key: construct_public_key(public_key_kind, &public_key)?,
                };
                near_action::Action::DeleteKey(action)
            }
```
