Found a solid analog. This is a genuine, reachable bug in `runtime/near-wallet-contract`, which is the contract code deployed for eth-implicit accounts on NEAR.

### Title
Relayer's attached deposit becomes permanently stuck in the Wallet Contract when the "invalid target" edge case is hit in `address_check_callback` - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The `WalletContract` (deployed on eth-implicit accounts to emulate Ethereum transactions on NEAR) accepts a `#[payable]` deposit from a relayer/caller in `rlp_execute` and tracks it via `CallerDeposit` so that it can be refunded if the intended cross-contract action later fails. One specific error branch inside the `address_check_callback` never issues this refund, permanently trapping the caller's attached NEAR in the contract, mirroring the reported Bonding.sol pattern where an edge case is handled in one code path but forgotten in a sibling path, leaving user value stuck with no recovery mechanism.

### Finding Description
`rlp_execute` is `#[payable]` and accepts a deposit from whichever account calls it (often a relayer relaying the eth-user's signed transaction, not the eth account itself): [1](#0-0) 

`CallerDeposit::new` is used precisely to remember this "value that must eventually be refunded if we can't complete the action," but only for external (non-self) callers: [2](#0-1) 

Because attached deposits are credited to the receiving account's balance by the protocol as soon as the `FunctionCall` action executes successfully (no panic occurs here — `rlp_execute` returns a normal `ExecuteResponse`/`Promise` value rather than panicking), the protocol will NOT auto-refund the deposit on a logical/business-level failure. The contract must explicitly create a refund `Promise` in every failure branch. This is correctly done in the "happy" failure path of `rlp_execute_callback`: [3](#0-2) 

However, in `address_check_callback`, when the address-registrar lookup determines the `target` address actually corresponds to an existing named account and the caller is not the current account itself, the code returns an error `ExecuteResponse` directly **without ever forwarding/refunding `caller_deposit`**: [4](#0-3) 

At this point `caller_deposit` (containing the relayer's `account_id` and `yocto_near` amount) is simply dropped — the value is never used again, and no `promise_batch_action_transfer` is issued to return it. The deposit remains part of the wallet contract's account balance forever, exactly analogous to the LP tokens getting stuck in `Bonding.sol` when the Uniswap handler's edge case (`amountMalt == 0 || amountReward == 0`) transfers tokens back to `Bonding.sol` without any code path to forward them to the user.

### Impact Explanation
This causes unauthorized, permanent loss of an unprivileged relayer/caller's NEAR balance — the deposit they attached to `rlp_execute` is credited into the wallet contract's account and never returned, with no owner-level recovery function in this contract. This is a concrete loss-of-funds impact directly reachable from normal transaction submission by any account acting as a relayer, not requiring any validator/node privilege.

### Likelihood Explanation
The trigger only requires: (1) a relayer (any account distinct from the wallet contract's own eth-implicit account) submits an `rlp_execute` call with a non-zero attached deposit, targeting an eth address requiring `address_check`, and (2) the address registrar's `lookup` resolves to `Some(account_id)` (i.e., the address actually corresponds to an existing named NEAR account) while `env::signer_account_id() != current_account_id` (a normal relayed transaction, not a self-submitted one). This is a realistic, commonly hit condition for relayers servicing base-token transfers to addresses that turn out to be registered accounts, not a contrived edge case requiring adversarial control of the protocol.

### Recommendation
In the `address_check_callback` "Invalid target" branch, forward the `caller_deposit` back to its owner via a `Promise`/`promise_batch_action_transfer` before returning the error `ExecuteResponse`, mirroring the refund logic already present in `rlp_execute_callback`'s `PromiseResult::Failed` arm.

### Proof of Concept
1. Relayer account `R` calls `rlp_execute(target, tx_bytes_b64)` on eth-implicit wallet contract `W` with attached deposit `D` NEAR, where `predecessor_account_id = R != current_account_id = W`, so `CallerDeposit::new` returns `Some({ account_id: R, yocto_near: D })`.
2. The parsed transaction is an `EOABaseTokenTransfer` with `address_check: Some(address)`, causing a promise to the address registrar followed by `address_check_callback(target, action, Some(CallerDeposit{R, D}))`.
3. The registrar lookup returns `Some(existing_account_id)` (the target address actually maps to a real named account) and `env::signer_account_id() != current_account_id` (a genuine relayed transaction, not self-submitted).
4. Code hits the `else` branch at `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs:167-173`, returning `PromiseOrValue::Value(ExecuteResponse{ success: false, ... })` — `caller_deposit` is never used to create a refund `Promise`.
5. `R`'s deposit `D` remains permanently credited to `W`'s account balance; there is no method in `WalletContract` allowing `R` to reclaim it.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L88-114)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L160-192)
```rust
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
