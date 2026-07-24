### Title
Sub-unit Transfer Amount Normalizes to Zero, Permanently Locking Already-Burned Tokens — (`near/omni-bridge/src/lib.rs`)

### Summary

When a user initiates an outbound transfer from NEAR to a destination chain whose token has fewer decimals, the bridge burns/locks the user's tokens during `init_transfer_internal` **before** any check that the decimal-normalized transfer amount is non-zero. The zero-amount guard lives exclusively in `sign_transfer`, which is called later by a relayer. Once `sign_transfer` reverts with `ERR_INVALID_AMOUNT_TO_TRANSFER`, the transfer is permanently stuck in `pending_transfers` with no cancel or refund path, and the user's tokens are irrecoverably burned.

### Finding Description

**Step 1 — Tokens are burned/locked unconditionally in `init_transfer_internal`.**

`init_transfer` validates only that `fee.fee < amount` (line 558–561), then calls `init_transfer_internal`, which burns or locks the full token amount before any normalization check: [1](#0-0) 

**Step 2 — `normalize_amount` uses floor division.**

The helper divides by `10^(origin_decimals − decimals)`. For a token registered with 24 NEAR decimals targeting a 6-decimal destination chain, the divisor is `10^18`. Any `amount_without_fee < 10^18` (i.e., less than 1 whole token unit on the destination) normalizes to zero: [2](#0-1) 

**Step 3 — `sign_transfer` permanently reverts for the stuck transfer.**

The zero-amount guard fires in `sign_transfer`, which is the only function that can advance the transfer to the MPC signing stage: [3](#0-2) 

Every subsequent call to `sign_transfer` for this `transfer_id` will revert identically. There is no public `cancel_transfer`, `refund_transfer`, or DAO rescue function that removes a `pending_transfers` entry and returns the burned tokens.

**Step 4 — No recovery path exists.**

`remove_transfer_message` is called only from:
- `sign_transfer_callback` — unreachable because `sign_transfer` panics before reaching the MPC call
- `claim_fee_callback` — requires a proof of a `FinTransfer` event on the destination chain, which never exists
- `process_fin_transfer_to_near` — same requirement

The `storage_unregister(force=true)` path removes the storage balance record but does not touch `pending_transfers` or restore burned tokens. [4](#0-3) 

### Impact Explanation

**Critical — Irreversible fund lock.** The user's tokens are burned by the bridge contract and the corresponding `pending_transfers` entry can never be cleared. The funds are permanently unclaimable. This matches the allowed impact: *"Irreversible fund lock, frozen redemption path, or permanently unclaimable user or protocol value in bridge, token, fee, vault, fast-transfer, or UTXO flows."*

### Likelihood Explanation

**Medium.** The condition is triggered whenever:
1. A token is registered with a large decimal difference between NEAR and the destination chain (e.g., 24 NEAR decimals → 6 EVM decimals, divisor = `10^18`).
2. The user sends an amount smaller than one destination-chain unit (e.g., less than `10^18` yoctoNEAR-equivalent, i.e., less than 1 whole token on the destination).

This is a realistic scenario for any stablecoin or low-decimal ERC-20 bridged through NEAR. The NEAR `init_transfer` path has no `amount > 0` guard analogous to the EVM/Starknet/Aptos implementations, and no minimum-amount check against the normalization factor. [5](#0-4) 

Compare with Starknet and Aptos, which both explicitly assert `amount > 0` at deposit time but still lack the normalization pre-check: [6](#0-5) [7](#0-6) 

### Recommendation

Add a normalization pre-check inside `init_transfer` (or `init_transfer_internal`) **before** burning or locking tokens:

```rust
let normalized = Self::normalize_amount(
    transfer_message.amount_without_fee().near_expect(BridgeError::InvalidFee),
    decimals,
);
require!(normalized > 0, BridgeError::InvalidAmountToTransfer.as_ref());
```

This requires looking up `token_decimals` at `init_transfer` time, which is already done in `sign_transfer`. Alternatively, add a public `cancel_transfer` entry point (callable by the original sender) that removes the `pending_transfers` entry and mints/unlocks the tokens back to the sender.

### Proof of Concept

1. Register a token with `origin_decimals = 24`, `decimals = 6` (divisor = `10^18`).
2. User calls `ft_transfer_call` with `amount = 500_000_000_000_000_000` (0.5 NEAR-equivalent, < `10^18`) and `fee = 0`.
3. `init_transfer` passes the `fee < amount` check (0 < 5×10^17 ✓).
4. `init_transfer_internal` burns the 5×10^17 tokens and stores the transfer.
5. Relayer calls `sign_transfer(transfer_id, ...)`.
6. `normalize_amount(5×10^17, {24, 6}) = 5×10^17 / 10^18 = 0`.
7. `require!(0 > 0, ...)` panics with `ERR_INVALID_AMOUNT_TO_TRANSFER`.
8. The transfer remains in `pending_transfers` forever; the 5×10^17 tokens are permanently burned. [8](#0-7)

### Citations

**File:** near/omni-bridge/src/lib.rs (L479-489)
```rust
        let amount_to_transfer = Self::normalize_amount(
            transfer_message
                .amount_without_fee()
                .near_expect(BridgeError::InvalidFee),
            decimals,
        );

        require!(
            amount_to_transfer > 0,
            BridgeError::InvalidAmountToTransfer.as_ref()
        );
```

**File:** near/omni-bridge/src/lib.rs (L558-561)
```rust
        require!(
            transfer_message.fee.fee < transfer_message.amount,
            BridgeError::InvalidFee.as_ref()
        );
```

**File:** near/omni-bridge/src/lib.rs (L652-672)
```rust
    #[private]
    pub fn sign_transfer_callback(
        &mut self,
        #[callback_result] call_result: Result<SignatureResponse, PromiseError>,
        #[serializer(borsh)] message_payload: TransferMessagePayload,
        #[serializer(borsh)] fee: &Fee,
    ) {
        if let Ok(signature) = call_result {
            if fee.is_zero() {
                self.remove_transfer_message(message_payload.transfer_id);
            }

            env::log_str(
                &OmniBridgeEvent::SignTransferEvent {
                    signature,
                    message_payload,
                }
                .to_log_string(),
            );
        }
    }
```

**File:** near/omni-bridge/src/lib.rs (L1834-1870)
```rust
    fn init_transfer_internal(
        &mut self,
        transfer_message: TransferMessage,
        storage_owner: AccountId,
    ) -> U128 {
        let required_storage_balance = self
            .add_transfer_message(transfer_message.clone(), storage_owner.clone())
            .saturating_add(NearToken::from_yoctonear(transfer_message.fee.native_fee.0));

        if self
            .try_update_storage_balance(
                storage_owner,
                required_storage_balance,
                NearToken::from_yoctonear(0),
            )
            .is_err()
        {
            self.remove_transfer_message_without_refund(transfer_message.get_transfer_id());
            return transfer_message.amount;
        }

        if let OmniAddress::Near(token_id) = transfer_message.token.clone() {
            self.burn_tokens_if_needed(token_id.clone(), transfer_message.amount);

            self.lock_tokens_if_needed(
                transfer_message.get_destination_chain(),
                &token_id,
                transfer_message.amount.0,
            );
        } else {
            self.remove_transfer_message_without_refund(transfer_message.get_transfer_id());
            return transfer_message.amount;
        }

        env::log_str(&OmniBridgeEvent::InitTransferEvent { transfer_message }.to_log_string());
        U128(0)
    }
```

**File:** near/omni-bridge/src/lib.rs (L2786-2792)
```rust
    /// Uses floor division — any sub-unit remainder ("dust") is truncated and not transferred
    /// to the destination chain. When fee > 0, dust is absorbed into the fee via `claim_fee`.
    /// When fee = 0, dust stays locked/burned. See SECURITY.md for details.
    fn normalize_amount(amount: u128, decimals: Decimals) -> u128 {
        let diff_decimals: u32 = (decimals.origin_decimals - decimals.decimals).into();
        amount / (10_u128.pow(diff_decimals))
    }
```

**File:** starknet/src/omni_bridge.cairo (L292-293)
```text
            assert(amount > 0, 'ERR_ZERO_AMOUNT');
            assert(fee < amount, 'ERR_INVALID_FEE');
```

**File:** aptos/sources/omni_bridge.move (L502-503)
```text
        assert!(amount > 0, E_ZERO_AMOUNT);
        assert!(fee < amount, E_INVALID_FEE);
```
