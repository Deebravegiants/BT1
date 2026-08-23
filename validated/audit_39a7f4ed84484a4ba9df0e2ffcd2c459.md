I have sufficient evidence to write the final analysis.

### Title
Relayer fee is paid out via an independent, unconditional receipt before the underlying transfer/call outcome is known - ([File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs])

### Summary
In the `near-wallet-contract` (deployed to eth-implicit accounts to emulate Ethereum transactions on NEAR), `inner_rlp_execute` dispatches a relayer-fee `Transfer` action to the relayer *before* creating/awaiting the promise for the user's actual intended action (an emulated base-token transfer or ERC-20 transfer). Because the fee-payment receipt is created as an independent, unchained promise batch rather than a continuation gated on the outcome of the main action, the relayer is paid even if the user's underlying transfer subsequently fails.

### Finding Description
`inner_rlp_execute` in [1](#0-0)  creates a standalone relayer-fee transfer receipt as soon as the transaction is parsed, whenever the parsed action is an `EOABaseTokenTransfer` or `ERC20Transfer` with a non-zero `fee`:

```rust
if !fee.is_zero() && context.predecessor_account_id != context.current_account_id {
    let refund_promise = env::promise_batch_create(&context.predecessor_account_id);
    env::promise_batch_action_transfer(refund_promise, *fee);
}
```

This call to `env::promise_batch_create` / `env::promise_batch_action_transfer` produces an independent NEAR receipt — it is not `.then()`-chained onto the promise for the real action (the ERC-20 `ft_transfer`/base-token transfer built later in the same function, `action_to_promise(...).then(ext.rlp_execute_callback(...))`, see [2](#0-1)  and [3](#0-2) ). On NEAR, sibling receipts created within the same function-call execution are dispatched and executed independently; a later receipt's failure does not roll back an earlier, already-created sibling receipt.

The contract *does* have a proper failure-handling path for the main action: `rlp_execute_callback` checks `env::promise_result(0)` and, on `PromiseResult::Failed`, refunds the `caller_deposit` (the value that was meant to reach the receiver) — see [4](#0-3) . However, this refund logic only covers the `deposit`/`CallerDeposit` amount, not the relayer fee — the relayer-fee transfer was already unconditionally dispatched at parse time in `inner_rlp_execute`, independent of whatever `rlp_execute_callback` later decides. So if the main token transfer or base-token transfer fails (e.g., the target ERC-20 contract panics on `ft_transfer`, insufficient balance, receiver not registered and `storage_deposit` fails, gas exhaustion in the chained call, etc.), the relayer still keeps the fee it was paid for a transaction that did not accomplish its intended effect.

This directly mirrors the reported bug class: a value-transfer/fee outcome is not gated on confirmation that the corresponding underlying operation actually succeeded, so a beneficiary (here, the relayer) can be credited even when the transfer it was compensating for fails.

### Impact Explanation
Funds (the user's `fee` deposit) are unconditionally paid to the relayer regardless of whether the compensated action (the actual token/NEAR transfer to the intended receiver) succeeds. This is a fund-loss condition for the user: they pay the relayer's fee but may not receive the intended effect of their transaction (e.g., their ERC-20 tokens are not actually transferred to the receiver, or their NEAR is not moved), while the relayer's compensation for delivering that transaction is paid out regardless. Given the code comment states "Relayers should also verify the fee before sending to make sure the user's signed transaction will refund enough to cover the relayer's gas costs", the fee is explicitly designed to be earned only for correctly relaying a transaction; the current implementation does not enforce that condition on-chain.

### Likelihood Explanation
This requires the fee to be non-zero and the underlying action to fail after the fee transfer has already been dispatched (e.g., a malformed/expired ERC-20 call, insufficient token balance on the wallet contract, or gas exhaustion in the multi-step ERC-20 storage-deposit + transfer chain). Such failures are plausible in normal operation (e.g., a relayer submits a transaction whose token balance changed since signing, or a receiver's storage-deposit step runs out of prepaid gas), making this a moderately likely event rather than requiring adversarial conditions, but it is not triggerable by an unprivileged attacker forcing arbitrary loss beyond their own fee.

### Recommendation
Chain the relayer-fee transfer onto the same promise as the main action (or move it into `rlp_execute_callback` gated on `PromiseResult::Successful`), so that the relayer is only compensated once the underlying transfer/call is confirmed to have succeeded. Alternatively, track the fee similarly to `CallerDeposit` and refund/withhold it in `rlp_execute_callback` when `PromiseResult::Failed` is observed.

### Proof of Concept
1. A user signs an Ethereum-emulated ERC-20 `transfer` transaction via their NEAR eth-implicit wallet contract, specifying a non-zero relayer `fee`.
2. A relayer submits it via `rlp_execute`. `inner_rlp_execute` immediately fires `promise_batch_action_transfer(refund_promise, fee)` to the relayer (`runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs:382-384`).
3. Separately, the contract queries `storage_balance_of` and then attempts `ft_transfer`/`storage_deposit`+`ft_transfer` on the target token contract via `action_to_promise(...).then(ext.rlp_execute_callback(...))`.
4. If the token transfer fails (e.g., insufficient token balance, target contract panics, or gas runs out in the two-hop `storage_deposit`+`ft_transfer` chain), `rlp_execute_callback` observes `PromiseResult::Failed` and only refunds `caller_deposit` (the NEAR attached deposit), not the already-paid relayer fee.
5. Net effect: the relayer receives `fee` in NEAR tokens even though the user's ERC-20 transfer never took effect.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L296-316)
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L367-385)
```rust
            // If the action is an emulated base token or ERC-20 transfer with a non-zero fee then
            // create a promise to send the refund to the relayer. This allows any relayer
            // to safely serve base token transfers from any wallet without additional
            // on-boarding because the relayer will receive some compensation for sending
            // the transaction. Users should always verify the fee before signing a base token
            // transfer. Relayers should also verify the fee before sending to make sure the
            // user's signed transaction will refund enough to cover the relayer's gas costs.
            if let TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
                fee,
                ..
            })
            | TransactionKind::EthEmulation(EthEmulationKind::ERC20Transfer { fee, .. }) =
                &transaction_kind
            {
                if !fee.is_zero() && context.predecessor_account_id != context.current_account_id {
                    let refund_promise = env::promise_batch_create(&context.predecessor_account_id);
                    env::promise_batch_action_transfer(refund_promise, *fee);
                }
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L433-458)
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
        }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L459-472)
```rust
        TransactionKind::EthEmulation(EthEmulationKind::SelfBaseTokenTransfer) => {
            // Base token transfers to self are no-ops on Near, so we do not need to
            // schedule an additional call. We can simply go straight to `rlp_execute_callback`.
            let ext: WalletContractExt =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            ext.rlp_execute_callback(caller_deposit)
        }
        _ => {
            let ext =
                WalletContract::ext(current_account_id).with_static_gas(RLP_EXECUTE_CALLBACK_GAS);
            action_to_promise(target, action)?.then(ext.rlp_execute_callback(caller_deposit))
        }
    };
    Ok(promise)
```
