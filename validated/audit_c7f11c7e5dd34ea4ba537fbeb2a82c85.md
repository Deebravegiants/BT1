### Title
Sub-Dust Amount Causes Permanent Fund Lock with No Recovery Path - (`File: near/omni-bridge/src/lib.rs`)

### Summary

When a user initiates a NEAR-side outbound transfer with an amount (minus fee) smaller than `10^(origin_decimals - decimals)`, the tokens are burned or locked in `init_transfer_internal` before any normalization check occurs. The subsequent `sign_transfer` call then permanently panics with `ERR_INVALID_AMOUNT_TO_TRANSFER` because `normalize_amount` floors the value to zero. No cancellation or refund path exists, leaving the user's tokens irreversibly locked.

### Finding Description

`normalize_amount` performs integer floor division: [1](#0-0) 

For a token registered with `origin_decimals = 24` and `decimals = 18`, `diff_decimals = 6`, so any `amount_without_fee < 1_000_000` normalizes to `0`.

`sign_transfer` correctly rejects this with a `require!`: [2](#0-1) 

However, by the time `sign_transfer` is called, `init_transfer_internal` has already burned or locked the tokens: [3](#0-2) 

The `init_transfer` entry point only validates `fee < amount`: [4](#0-3) 

There is no pre-check that `normalize_amount(amount - fee) > 0` before tokens are consumed.

### Impact Explanation

Once `init_transfer_internal` succeeds, the transfer message sits in `pending_transfers`. `sign_transfer_callback` only removes the message when MPC signing **succeeds** and `fee.is_zero()`: [5](#0-4) 

Since `sign_transfer` panics before reaching MPC, no signature is ever produced. Without a signature, no `fin_transfer` can execute on the destination chain, so `claim_fee_callback` (the other removal path) is also unreachable: [6](#0-5) 

There is no `cancel_transfer` or admin-rescue function. For deployed (bridge-minted) tokens, the burn at line 1856 is irreversible. For native locked tokens, the locked balance counter is incremented and can never be decremented without a `fin_transfer` proof. The user's funds are permanently unclaimable.

### Likelihood Explanation

The condition requires:
1. A token pair where `origin_decimals > decimals` (e.g., a 24-decimal NEAR token bridging to an 18-decimal EVM representation — a realistic configuration).
2. The user sends `amount - fee < 10^(origin_decimals - decimals)` base units.

For the 24→18 example, any transfer of fewer than 1,000,000 base units (i.e., less than 0.000001 tokens) triggers the lock. A user sending a small test amount or a dust amount via an automated system can hit this silently — `ft_transfer_call` returns `U128(0)` (success), the `InitTransferEvent` is emitted, and the failure only surfaces later when the relayer's `sign_transfer` call panics.

### Recommendation

Add a normalization pre-check inside `init_transfer` (or `init_transfer_internal`) **before** burning or locking tokens:

```rust
// In init_transfer, after building transfer_message:
if let Some(token_address) = self.get_token_address(
    transfer_message.get_destination_chain(),
    self.get_token_id(&transfer_message.token),
) {
    if let Some(decimals) = self.token_decimals.get(&token_address) {
        let normalized = Self::normalize_amount(
            transfer_message.amount_without_fee()
                .near_expect(BridgeError::InvalidFee),
            decimals,
        );
        require!(normalized > 0, BridgeError::InvalidAmountToTransfer.as_ref());
    }
}
```

Alternatively, add a `cancel_transfer` function gated to the original sender that removes the pending entry and returns locked/minted tokens.

### Proof of Concept

1. Register a token with `origin_decimals = 24`, `decimals = 18` (`diff_decimals = 6`).
2. User calls `ft_transfer_call` with `amount = 500_000` (< 10^6), `fee = 0`.
3. `init_transfer_internal` succeeds: tokens are burned/locked, `InitTransferEvent` emitted.
4. Trusted relayer calls `sign_transfer` for this `transfer_id`.
5. `normalize_amount(500_000, {origin: 24, dest: 18}) = 500_000 / 1_000_000 = 0`.
6. `require!(0 > 0, ...)` panics → `ERR_INVALID_AMOUNT_TO_TRANSFER`.
7. No signature produced. Transfer message stays in `pending_transfers` forever.
8. User's 500,000 base-unit tokens are permanently lost. [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** near/omni-bridge/src/lib.rs (L659-662)
```rust
        if let Ok(signature) = call_result {
            if fee.is_zero() {
                self.remove_transfer_message(message_payload.transfer_id);
            }
```

**File:** near/omni-bridge/src/lib.rs (L1098-1098)
```rust
        let transfer_message = self.remove_transfer_message(fin_transfer.transfer_id);
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
