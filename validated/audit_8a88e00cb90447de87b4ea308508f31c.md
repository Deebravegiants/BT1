### Title
Attached NEAR deposit is never refunded when the intermediate promise of an ERC-20 relayed transfer (or address-registrar check) fails - ([File: runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs])

### Summary
The `WalletContract` (Eth-implicit account "wallet contract") shipped in nearcore accepts an attached NEAR deposit from an external caller and tracks it in a `CallerDeposit` so it can be refunded if the relayed cross-contract call fails [1](#0-0) . The final callback, `rlp_execute_callback`, correctly implements this refund when the promise it is chained to fails [2](#0-1) . However, two intermediate callbacks used for multi-step Ethereum-emulated flows — `address_check_callback` and `nep_141_storage_balance_callback` — drop the `caller_deposit` and return a failure `ExecuteResponse` without issuing any refund when their respective preliminary calls (`AddressRegistrar::lookup` or NEP-141 `storage_balance_of`) fail [3](#0-2) [4](#0-3) .

### Finding Description
`rlp_execute` is `#[payable]`, so a caller (a relayer or any predecessor) can attach a NEAR deposit when submitting a relayed Ethereum-style transaction [5](#0-4) . `inner_rlp_execute` builds a `CallerDeposit` capturing that attached deposit for later refund purposes whenever the predecessor is not the contract itself [6](#0-5) .

For two of the supported transaction kinds — `EOABaseTokenTransfer` with an address check, and `ERC20Transfer` — execution is a multi-step promise chain:
1. `EOABaseTokenTransfer{address_check: Some(_)}` first calls the address registrar, then `.then(ext.address_check_callback(target, action, caller_deposit))` [7](#0-6) .
2. `ERC20Transfer` first calls `storage_balance_of` on the token contract, then `.then(ext.nep_141_storage_balance_callback(token_id, receiver_id, action, caller_deposit))` [8](#0-7) .

In both callbacks, if the preliminary promise result is `PromiseResult::Failed` (e.g., the registrar contract call runs out of gas / panics, or the token contract's `storage_balance_of` call fails or the token account doesn't exist), the callback simply returns an `ExecuteResponse{success: false, ...}` and discards `caller_deposit` — it is received as a function parameter but never used on this path [9](#0-8) [10](#0-9) . This is inconsistent with `rlp_execute_callback`, which is reached in the single-step case and does the correct thing — creating a `Transfer` promise back to `caller_deposit.account_id` for `caller_deposit.yocto_near` on failure [2](#0-1) .

Since the deposit was already attached (deducted from the caller and credited to the wallet-contract's account balance) at the time `rlp_execute` was called, failing to issue a refund receipt means those tokens are stranded in the wallet contract's balance with no code path that returns them to the original caller. This mirrors exactly the bug class in the external report: `_executeWithToken`-style intermediate failure with no recovery/refund path for attached value.

### Impact Explanation
Any external account that calls `rlp_execute` with an attached NEAR deposit targeting an `ERC20Transfer` (which is the common relayer-fee-refund pattern used throughout this contract, see `fee` handling in `inner_rlp_execute` [11](#0-10) ) or a base-token transfer to an unregistered eth-implicit target can permanently lose the attached deposit if the preliminary cross-contract call (`storage_balance_of` or the address-registrar `lookup`) fails. This is a genuine, non-recoverable balance loss for an unprivileged account interacting with a shipped nearcore contract (the Eth-implicit account "wallet contract"), reachable purely through normal transaction submission — no validator/node privilege required.

### Likelihood Explanation
The preliminary calls can fail for reasons outside the caller's control: the token contract may not implement `storage_balance_of`, may run out of allotted gas (`NEP_141_STORAGE_BALANCE_OF_GAS` is a fixed 5 Tgas budget [12](#0-11) , insufficient for some contracts), may not exist, or may panic; similarly the address registrar lookup can fail. These are realistic, easily triggered conditions (e.g., relaying to a nonexistent or misbehaving NEP-141 token), making this readily reachable in normal operation, not merely a theoretical edge case.

### Recommendation
In `address_check_callback` and `nep_141_storage_balance_callback`, mirror the refund logic already present in `rlp_execute_callback`: on `PromiseResult::Failed`, if `caller_deposit` is `Some`, create a `promise_batch_transfer` back to `caller_deposit.account_id` for `caller_deposit.yocto_near` before returning the failure `ExecuteResponse`.

### Proof of Concept
1. Deploy an eth-implicit `WalletContract` and fund it with the address-mapping needed to pass `validate_tx_relayer_data`.
2. As an external relayer account `R` (`predecessor_account_id != current_account_id`), call `rlp_execute(target, tx_bytes_b64)` attaching a NEAR deposit `D`, where the RLP transaction decodes to an `ERC20Transfer` (`FUNCTION_CALL_SELECTOR`/emulated `transfer` selector on a token contract) targeting a `receiver_id` that is not registered with the token (so the `Some`/`None` storage-balance branch is exercised) — see `inner_rlp_execute`'s `ERC20Transfer` arm building the promise chain to `nep_141_storage_balance_callback` [8](#0-7) .
3. Make the token account `token_id` either not exist or panic on `storage_balance_of` (e.g., point `target`/`token_id` at an account with no deployed contract).
4. The `storage_balance_of` promise fails, `nep_141_storage_balance_callback` is invoked with `PromiseResult::Failed`, and it returns `ExecuteResponse{success:false,...}` without creating any transfer back to `R` [4](#0-3) .
5. Query `R`'s balance: deposit `D` is not returned; it remains stuck in the wallet contract's account balance permanently, with no other codepath able to reclaim it for `R`.

### Citations

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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L35-35)
```rust
const NEP_141_STORAGE_BALANCE_OF_GAS: Gas = Gas::from_tgas(5);
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L141-159)
```rust
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
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L203-221)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L330-346)
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L366-385)
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
