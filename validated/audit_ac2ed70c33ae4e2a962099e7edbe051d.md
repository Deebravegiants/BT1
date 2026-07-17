### Title
Attached NEAR Deposit Permanently Locked in `WalletContract::rlp_execute` on Early-Return Paths - (File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs)

### Summary
`WalletContract::rlp_execute` is marked `#[payable]` and accepts NEAR tokens attached to the call, but multiple early-return code paths return normally (without panicking) without refunding the attached deposit. In NEAR Protocol, only a panic triggers an automatic deposit refund; a normal return keeps the deposit in the contract. Any NEAR attached to `rlp_execute` in these paths is permanently credited to the wallet contract's balance and is irrecoverable by the caller.

### Finding Description
`rlp_execute` is the public entry point of `WalletContract` and is decorated `#[payable]`, allowing callers to attach NEAR tokens. [1](#0-0) 

The contract has a `CallerDeposit` mechanism that is supposed to refund the caller's deposit if the downstream cross-contract call fails. This mechanism is created inside `inner_rlp_execute` and threaded through to `rlp_execute_callback`. [2](#0-1) [3](#0-2) 

However, there are three code paths where the attached deposit is silently absorbed:

**Path 1 — `has_in_flight_tx` guard (most impactful):** The very first check in `rlp_execute` returns a `PromiseOrValue::Value(...)` (a normal, non-panicking return) before `inner_rlp_execute` is ever called and before `CallerDeposit` is created. Any NEAR attached to this call is never tracked and never refunded. [4](#0-3) 

**Path 2 — Error returns from `inner_rlp_execute`:** When `parse_rlp_tx_to_action` returns a user error or relayer error, `inner_rlp_execute` returns `Err(...)`. The `caller_deposit` created at line 345 is dropped. Back in `rlp_execute`, the `Err(e) => PromiseOrValue::Value(e.into())` arm returns normally without issuing any refund. [5](#0-4) [6](#0-5) 

**Path 3 — Ban-relayer promise path:** When `inner_rlp_execute` returns `Err(Error::Relayer(_))` and the signer is the wallet contract itself, a `create_ban_relayer_promise` is scheduled. The `ban_relayer` callback returns normally and contains no deposit refund logic. [7](#0-6) [8](#0-7) 

### Impact Explanation
Any NEAR tokens attached to `rlp_execute` in the above paths are immediately credited to the wallet contract's account balance by the NEAR runtime (deposit is applied before execution begins). Because the function returns normally rather than panicking, the runtime does not issue an automatic deposit refund. The caller's NEAR balance is permanently reduced by the deposit amount. The corrupted state is the caller's on-chain NEAR balance (reduced) and the wallet contract's on-chain NEAR balance (increased by the same amount). The caller has no mechanism to recover these funds.

### Likelihood Explanation
Path 1 is the most realistic trigger. During normal wallet operation, `has_in_flight_tx` is `true` for the entire duration of a cross-contract call (which can span multiple blocks). Any external caller — such as a relayer funding a cross-contract call — who attaches NEAR and submits `rlp_execute` during this window loses their deposit. The caller cannot observe `has_in_flight_tx` atomically before submitting; the state can change between their view query and their transaction landing. Relayers are explicitly expected to attach deposits to fund user actions (the `CallerDeposit` type exists precisely for this use case), making this a realistic loss scenario.

### Recommendation
In the `has_in_flight_tx` early-return path, check `env::attached_deposit()` and, if non-zero, issue a refund transfer to `env::predecessor_account_id()` before returning. Apply the same pattern to the `Err(e) => PromiseOrValue::Value(e.into())` arm and the ban-relayer path. Alternatively, remove `#[payable]` from `rlp_execute` and require callers to fund cross-contract calls through a separate mechanism, mirroring the fix applied to `sendZkSafeTransaction` in the reference report.

### Proof of Concept
1. Wallet owner submits a valid `rlp_execute` call that triggers a cross-contract call (e.g., an ERC-20 transfer). `has_in_flight_tx` becomes `true`.
2. Before the cross-contract call resolves (within the same or next block), an external relayer submits `rlp_execute` with `attached_deposit = 5 NEAR` to fund a subsequent action.
3. `rlp_execute` hits the `has_in_flight_tx` guard at line 97 and returns `PromiseOrValue::Value(ExecuteResponse { success: false, ... })` — a normal return.
4. The NEAR runtime does not refund the deposit (no panic occurred). The 5 NEAR is credited to the wallet contract's balance.
5. The relayer's account balance is permanently reduced by 5 NEAR with no recourse. [9](#0-8) [10](#0-9)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-128)
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L340-345)
```rust
    let context = ExecutionContext::new(
        current_account_id.clone(),
        predecessor_account_id,
        env::attached_deposit(),
    )?;
    let caller_deposit = CallerDeposit::new(&context);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L389-409)
```rust
        Err(err @ Error::User(_)) => {
            // Increment nonce on all user errors to prevent replay.
            *nonce = nonce.saturating_add(1);
            return Err(err);
        }
        Err(err) => {
            // Do not increment nonce on Relayer or AccountId errors.
            // The latter error is an issue in the deployment (so the nonce is meaningless).
            // The former arises from the relayer itself doing something wrong and thus the
            // user's transaction could still be valid and potentially submitted properly by
            // another relayer. To allow this we do not increment the nonce.
            //
            // Note: if a relayer is using an access key for this wallet then that key will
            // still be revoked (in the main logic of `rlp_execute`). This fact together with
            // the condition that there only be one in-flight transaction at a time implies
            // that a relayer cannot maliciously burn a large portion of the user's tokens.
            // If the relayer is not using an access key then they are spending their own
            // resources on the gas and therefore we do not care if the relayer submits
            // the same faulty transaction multiple times.
            return Err(err);
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/types.rs (L180-192)
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
}
```
