### Title
Relayer Fee Paid Unconditionally Before NEP-141 `ft_transfer` Outcome Is Known — (`File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
In the Wallet Contract's `inner_rlp_execute` function, the relayer fee is transferred to the relayer as an independent promise batch action **before** the NEP-141 `ft_transfer` is executed or its result is known. If the `ft_transfer` subsequently fails (e.g., insufficient FT balance, token contract panic, or `storage_balance_of` failure), the fee is not refunded. This is the direct analog of the reported ERC-20 `transferFrom` unchecked-return-value bug: a payment that should be atomic with the underlying transfer is instead unconditional, allowing the relayer to collect a fee for a transfer that never occurred, at the wallet owner's expense.

### Finding Description

In `inner_rlp_execute`, for both `EthEmulationKind::EOABaseTokenTransfer` and `EthEmulationKind::ERC20Transfer` with a non-zero fee, the following code runs unconditionally:

```rust
if !fee.is_zero() && context.predecessor_account_id != context.current_account_id {
    let refund_promise = env::promise_batch_create(&context.predecessor_account_id);
    env::promise_batch_action_transfer(refund_promise, *fee);
}
``` [1](#0-0) 

This schedules an independent NEAR transfer of `fee` yoctoNEAR from the wallet's balance to the relayer (`predecessor_account_id`). This promise batch is **not** chained to the `ft_transfer` promise — it executes regardless of whether the subsequent NEP-141 transfer succeeds or fails.

The actual `ft_transfer` is dispatched later via `nep_141_storage_balance_callback`, which first calls `storage_balance_of` on the token contract, then conditionally calls `ft_transfer`, and finally calls `rlp_execute_callback`: [2](#0-1) 

In `rlp_execute_callback`, when `PromiseResult::Failed` is detected, only the `caller_deposit` (the NEAR attached by the relayer to the `rlp_execute` call) is refunded — the relayer fee is never returned: [3](#0-2) 

Additionally, in `nep_141_storage_balance_callback`, if `storage_balance_of` itself fails, the function returns early without ever reaching `rlp_execute_callback`, meaning neither the fee nor the `caller_deposit` is refunded: [4](#0-3) 

### Impact Explanation

The wallet owner's NEAR balance is incorrectly reduced by the fee amount even when the NEP-141 token transfer fails. The corrupted protocol value is the **wallet account's NEAR balance**: it is debited by `fee` yoctoNEAR without the corresponding FT transfer having occurred. The relayer's NEAR balance is correspondingly and incorrectly credited. This is a direct financial loss for the wallet owner.

### Likelihood Explanation

Any unprivileged external account can act as a relayer and call `rlp_execute`. A malicious relayer can:
1. Observe on-chain that the wallet's FT balance is insufficient for the requested transfer amount.
2. Submit a user-signed ERC-20 transfer transaction (with a non-zero `gas_price`/fee) that they know will fail.
3. Collect the fee from the wallet's NEAR balance while the FT transfer fails silently.

The nonce is incremented before the fee is paid (line 364), so each signed transaction can only be exploited once. However, if the user has signed multiple transactions with non-zero fees, a malicious relayer can submit all of them in sequence, collecting fees for each failed transfer. [5](#0-4) 

### Recommendation

The relayer fee transfer must be made conditional on the success of the underlying `ft_transfer`. Instead of scheduling the fee as an independent promise batch in `inner_rlp_execute`, the fee should be paid inside `rlp_execute_callback` only when `PromiseResult::Successful` is observed. The `fee` amount should be passed as a parameter to `rlp_execute_callback` (similar to how `caller_deposit` is already passed), and the transfer to the relayer should be scheduled only on the success branch.

### Proof of Concept

1. User signs an Ethereum ERC-20 transfer transaction with `gas_price > 0` and `gas_limit > 0`, targeting a NEP-141 token contract. The signed fee = `gas_price * gas_limit * MAX_YOCTO_NEAR` yoctoNEAR.
2. The wallet's FT balance for that token is 0 (or less than the transfer amount).
3. Malicious relayer calls `rlp_execute(target, tx_bytes_b64)` on the wallet contract.
4. `inner_rlp_execute` runs: nonce is incremented, then `env::promise_batch_action_transfer(refund_promise, fee)` is scheduled — fee is paid to the relayer from the wallet's NEAR balance.
5. The `storage_balance_of` → `nep_141_storage_balance_callback` → `ft_transfer` chain executes; `ft_transfer` panics due to insufficient balance.
6. `rlp_execute_callback` receives `PromiseResult::Failed`; only `caller_deposit` (if any) is refunded.
7. **Result**: Relayer receives `fee` yoctoNEAR from the wallet. Wallet's NEAR balance is reduced by `fee`. No FT tokens were transferred. [6](#0-5) [7](#0-6)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L203-210)
```rust
        let maybe_storage_balance: Option<StorageBalance> = match env::promise_result(0) {
            PromiseResult::Failed => {
                return PromiseOrValue::Value(ExecuteResponse {
                    success: false,
                    success_value: None,
                    error: Some(format!("Call to NEP-141 {token_id}::storage_balance_of failed")),
                });
            }
```

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L363-365)
```rust
            } else {
                *nonce = nonce.saturating_add(1);
            }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L374-385)
```rust
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
