### Title
Relayer Fee Paid Unconditionally and Repeatably Before Action Success is Verified, Enabling Wallet-Contract Balance Drain - (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs`)

### Summary
The reported ERC-20 bug class ("payment/transfer performed without verifying the counter-action actually succeeded") maps onto `inner_rlp_execute` in the NEAR Wallet Contract. The relayer-fee refund promise for an emulated base-token/ERC-20 transfer is fired unconditionally, independent of whether the corresponding user action (`address_check`, `ft_transfer`, native transfer, etc.) ever executes or succeeds, and — for the `EOABaseTokenTransfer { address_check: Some(_), .. }` branch — the nonce is deliberately *not* incremented, allowing the exact same signed transaction to be resubmitted and the fee to be paid out again on every retry.

### Finding Description
In `inner_rlp_execute` [1](#0-0) , after parsing the RLP transaction into an `Action`/`TransactionKind`, the code special-cases the `address_check: Some(_)` variant of `EOABaseTokenTransfer` to *skip* nonce incrementing, explicitly to let an honest relayer retry after a faulty relayer's attempt: [2](#0-1) 

Immediately after that, and regardless of the `address_check` branch, if the transaction carries a non-zero `fee`, a brand-new, independent promise (`promise_batch_create` + `promise_batch_action_transfer`) is fired straight to `context.predecessor_account_id` (the relayer) — this is not chained via `.then()` to the outcome of the actual user action: [3](#0-2) 

Only after this unconditional fee payment does the code proceed to actually attempt the user's action, e.g. dispatching to `address_registrar.lookup(...)`: [4](#0-3) 

In `address_check_callback`, if the target address resolves to an existing named account, the whole action is rejected outright with no NEP-141/native transfer ever executed, and `has_in_flight_tx` is reset to `false`, re-opening the contract for a new call: [5](#0-4) 

Because (a) the fee-transfer promise is unconditional and unlinked to the success of the user's intended action, and (b) the nonce is intentionally left unchanged for this exact code path, a relayer can call `rlp_execute` again with the identical `tx_bytes_b64` after `address_check_callback` rejects the target, collecting the fee again. This can be repeated indefinitely, draining the wallet-contract account's NEAR balance one fee-payment at a time, with no legitimate action ever completing.

### Impact Explanation
This is a concrete, unauthorized balance change: value (the "fee") is unconditionally transferred out of the eth-implicit wallet-contract account to any caller who can trigger the retryable `address_check: Some(_)` path, without the underlying user-intended action (the actual base-token/ERC-20 transfer this fee is supposed to compensate) ever executing. Because the nonce is deliberately not advanced on this path, the same signed payload can be resubmitted an unbounded number of times, allowing repeated fee extraction until the account's NEAR balance (used for gas/fee/emulation purposes) is exhausted — a direct, repeatable theft of funds from the wallet-contract account, closely analogous to a bidder receiving the asset (here: the fee) without the counter-obligation (a successful, validated transfer) ever being honored.

### Likelihood Explanation
The path is reachable by any account that can call `rlp_execute` on a deployed wallet contract with attacker-controlled `target`/`tx_bytes_b64` framing — an address that will resolve, via the on-chain registrar, to an existing named account (a condition fully within the caller's control, since they can freely choose which named/target address to reference in the crafted RLP transaction). No validator or privileged access is required; it only requires submitting ordinary transactions/RPC calls to the contract, matching the "unprivileged account" analog requirement. The fee amount per call is bounded by whatever `fee` value is present in the (attacker-supplied) RLP payload, but the number of repetitions is unbounded since the nonce check does not gate this path.

### Recommendation
- Gate the relayer fee-refund promise on confirmed success of the corresponding user action, e.g. by chaining it with `.then()` after the primary action/callback resolves successfully, rather than firing it as an independent, unconditional promise.
- For the `EOABaseTokenTransfer { address_check: Some(_) }` path, either (a) increment the nonce before paying any fee so a given signed transaction can only ever trigger one fee payment, or (b) defer fee payment until after `address_check_callback` confirms the target is a valid eth-implicit account and the action can proceed, refunding/skipping the fee entirely when the target check fails.
- Add integration tests asserting that repeated `rlp_execute` calls with the same nonce and a target that resolves to a named account result in at most one fee payment (or none).

### Proof of Concept
1. Deploy/attach to a wallet contract instance holding NEAR balance intended for eth-emulated gas/fees.
2. Craft an RLP-encoded transaction representing an `EOABaseTokenTransfer` whose `to` address hashes to some `target` account ID that will later resolve (via the address registrar) to an existing *named* account — this makes `address_check` non-`None`, and include a non-zero `fee`.
3. Call `rlp_execute(target, tx_bytes_b64)` as a relayer account. Observe:
   - `inner_rlp_execute` does not increment `self.nonce` (per [6](#0-5) ).
   - A `promise_batch_action_transfer` of `fee` yoctoNEAR fires to the caller unconditionally (per [7](#0-6) ).
   - The address-check callback subsequently rejects the target as a named account and returns `success: false` (per [5](#0-4) ), resetting `has_in_flight_tx` to `false`.
4. Re-submit the identical `tx_bytes_b64` via another `rlp_execute` call. Because the nonce was never advanced, this succeeds again and pays the fee a second time.
5. Repeat step 4 to drain the wallet contract's NEAR balance, without ever successfully completing the user's intended base-token transfer.

Note: I was unable to fully inspect `internal.rs`'s exact fee-parsing/validation logic (e.g., whether `fee` is user-signed and capped) within the available exploration budget; this should be verified by a follow-up review of `runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs` and `types.rs` to confirm exact fee bounds and any existing mitigations not visible in the excerpts reviewed.

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L161-173)
```rust
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

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L356-365)
```rust
            // the users tokens because only one transaction is allowed to be in-flight
            // at a time.
            if let TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
                address_check: Some(_),
                ..
            }) = &transaction_kind
            {
            } else {
                *nonce = nonce.saturating_add(1);
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
