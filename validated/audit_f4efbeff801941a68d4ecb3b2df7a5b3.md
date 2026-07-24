### Title
Dust Transfer Permanently Locks User Tokens Due to Missing Pre-Normalization Amount Check — (`near/omni-bridge/src/lib.rs`)

### Summary
The NEAR bridge's `init_transfer` accepts outbound transfers where the net amount (after fee) is smaller than the decimal normalization factor, causing `normalize_amount` to floor-divide to zero. The tokens are immediately locked/burned, but `sign_transfer` always panics with `InvalidAmountToTransfer` for such transfers, and no cancel/refund path exists. The user's tokens are permanently unclaimable.

### Finding Description

**Step 1 — Transfer accepted without normalization pre-check.**

`init_transfer` validates only that `fee.fee < amount`: [1](#0-0) 

There is no check that `normalize_amount(amount - fee, decimals) > 0`. For a token registered with `origin_decimals = 24` and `decimals = 6`, the normalization factor is `10^18`. Any transfer with `amount_without_fee < 10^18` normalizes to zero.

**Step 2 — Tokens are locked/burned immediately.**

`init_transfer_internal` locks or burns the full `transfer_message.amount` before any normalization check: [2](#0-1) 

**Step 3 — `sign_transfer` always panics for dust transfers.**

When the relayer later calls `sign_transfer`, `normalize_amount` is applied and the zero-amount check fires: [3](#0-2) 

`normalize_amount` uses floor division: [4](#0-3) 

The `require!` panics, reverting the relayer's transaction. The pending transfer entry remains in `pending_transfers` untouched.

**Step 4 — No recovery path exists.**

`remove_transfer_message` is only called from:
- `sign_transfer_callback` — never reached because `sign_transfer` panics before the MPC call
- `claim_fee_callback` — requires a `FinTransfer` proof from the destination chain, which never arrives because the transfer was never signed [5](#0-4) 

There is no public `cancel_transfer` or user-accessible refund function. The `pending_transfers` map has no expiry mechanism.

**The `normalize_amount` comment itself acknowledges the dust-lock design for sub-unit remainders:** [6](#0-5) 

However, this comment addresses sub-unit remainder dust (e.g., 1 unit out of 1,000,001). The vulnerability here is the entire transfer amount normalizing to zero — the user loses 100% of their transferred tokens, not a negligible remainder.

### Impact Explanation

User tokens are permanently locked in the bridge contract (for native tokens) or permanently burned (for deployed bridge tokens) with no on-chain recovery path. This matches the Critical impact criterion: **"Irreversible fund lock … or permanently unclaimable user … value in bridge … flows."**

The `pending_transfers` entry also permanently consumes storage, and the `locked_tokens` accounting is inflated by the dust amount, creating a permanent discrepancy between the accounting and the actual redeemable supply.

### Likelihood Explanation

Any unprivileged user can trigger this by calling `ft_transfer_call` on a registered token with a small amount. Tokens with large decimal differences (e.g., a 24-decimal NEAR-side token mapped to an 8-decimal EVM token, normalization factor `10^16`) are particularly susceptible. A user sending `1` base unit of such a token loses it permanently. This is realistic for:
- Tokens with large decimal gaps (common in cross-chain bridges)
- UI bugs or off-by-one errors in amount entry
- Automated scripts that don't pre-validate normalized amounts

### Recommendation

Add a normalization pre-check in `init_transfer` (or in `init_transfer_internal`) before locking/burning tokens:

```rust
// In init_transfer, after building transfer_message:
let token_address = self.get_token_address(
    transfer_message.get_destination_chain(),
    self.get_token_id(&transfer_message.token),
);
if let Some(addr) = token_address {
    if let Some(decimals) = self.token_decimals.get(&addr) {
        let normalized = Self::normalize_amount(
            transfer_message.amount_without_fee().near_expect(BridgeError::InvalidFee),
            decimals,
        );
        require!(normalized > 0, BridgeError::InvalidAmountToTransfer.as_ref());
    }
}
```

Alternatively, add a `cancel_transfer` function that allows the original sender to reclaim tokens from a pending transfer that has never been signed, subject to a time-lock.

### Proof of Concept

1. Register a token with `origin_decimals = 24`, `decimals = 6` (normalization factor = `10^18`).
2. Call `ft_transfer_call` with `amount = 999` (any value < `10^18`), `fee = 0`, destination = EVM chain.
3. `init_transfer` succeeds: `0 < 999` passes the fee check; `init_transfer_internal` locks 999 units and stores the pending transfer.
4. Relayer calls `sign_transfer` for this transfer ID.
5. `normalize_amount(999, {origin_decimals:24, decimals:6}) = 999 / 10^18 = 0`.
6. `require!(0 > 0, ...)` panics → transaction reverts.
7. Repeat step 4–6 indefinitely: always panics.
8. User's 999 units are permanently locked. No cancel function exists.

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

**File:** near/omni-bridge/src/lib.rs (L1855-1862)
```rust
        if let OmniAddress::Near(token_id) = transfer_message.token.clone() {
            self.burn_tokens_if_needed(token_id.clone(), transfer_message.amount);

            self.lock_tokens_if_needed(
                transfer_message.get_destination_chain(),
                &token_id,
                transfer_message.amount.0,
            );
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
