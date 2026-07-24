### Title
Sub-unit Transfer Amount Permanently Locks User Tokens Due to Missing Normalized-Amount Validation at Intake — (`near/omni-bridge/src/lib.rs`)

### Summary
The NEAR bridge accepts `init_transfer` calls for amounts that normalize to zero after decimal conversion, but `sign_transfer` later panics with `InvalidAmountToTransfer` when it detects the zero normalized amount. Because no cancellation or refund path exists for a stored pending transfer, the user's tokens are permanently locked in the bridge.

### Finding Description
The public entry point for NEAR-originated transfers is `ft_transfer_call` → `ft_on_transfer` → `init_transfer`. Inside `init_transfer`, the only fee-related validation is:

```rust
require!(
    transfer_message.fee.fee < transfer_message.amount,
    BridgeError::InvalidFee.as_ref()
);
``` [1](#0-0) 

There is no check that `normalize_amount(amount - fee) > 0`. When the transfer is accepted, `init_transfer_internal` locks or burns the tokens and stores the transfer in `pending_transfers`, returning `U128(0)` to the NEP-141 caller (meaning zero tokens are refunded): [2](#0-1) 

Later, when a trusted relayer calls `sign_transfer`, the function computes:

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
``` [3](#0-2) 

`normalize_amount` performs floor division:

```rust
fn normalize_amount(amount: u128, decimals: Decimals) -> u128 {
    let diff_decimals: u32 = (decimals.origin_decimals - decimals.decimals).into();
    amount / (10_u128.pow(diff_decimals))
}
``` [4](#0-3) 

For any token where `origin_decimals > decimals` (e.g., a token with 24 origin decimals bridged to 18 decimals, a common configuration), any transfer `amount - fee < 10^6` normalizes to zero. The `require!` at line 486–489 then panics, and `sign_transfer` is permanently blocked for that transfer ID. The transfer record remains in `pending_transfers` with no mechanism to cancel it or recover the locked tokens.

### Impact Explanation
**Critical — Irreversible fund lock.** Once `init_transfer_internal` returns `U128(0)`, the NEP-141 `ft_transfer_call` mechanism does not refund the tokens. The transfer is stored and the tokens are locked/burned. Because `sign_transfer` will always panic for this transfer (the normalized amount is structurally zero and cannot change), and no `cancel_transfer` or equivalent function exists in the contract, the user's tokens are permanently unclaimable.

### Likelihood Explanation
**Low.** The condition requires:
1. A token registered with `origin_decimals > decimals` (e.g., 24 vs 18, a 6-decimal gap).
2. A user sending an amount smaller than `10^(origin_decimals - decimals)` (e.g., less than 1,000,000 base units for a 6-decimal gap).

Both conditions are realistic in production: many ERC-20 tokens use 18 decimals while NEAR tokens use 24, and users may send dust amounts or make arithmetic errors. The protocol provides no warning at intake.

### Recommendation
Add a normalized-amount validation inside `init_transfer` (before tokens are locked) to reject transfers whose net amount normalizes to zero:

```rust
// After computing decimals for the destination token:
let normalized = Self::normalize_amount(
    transfer_message.amount_without_fee()?,
    decimals,
);
require!(normalized > 0, BridgeError::InvalidAmountToTransfer.as_ref());
```

This mirrors the guard already present in `sign_transfer` but moves it to the intake point where a clean revert (and automatic NEP-141 refund) is still possible.

### Proof of Concept
1. A token is registered with `origin_decimals = 24`, `decimals = 18` (6-decimal normalization gap).
2. Alice calls `ft_transfer_call` on the token contract with `amount = 500_000` (less than `10^6`), `fee = 0`, targeting the NEAR bridge.
3. `ft_on_transfer` → `init_transfer` passes the `fee < amount` check (0 < 500_000). `init_transfer_internal` locks 500_000 base units and stores the transfer. `ft_transfer_call` receives `U128(0)` back — no refund.
4. A trusted relayer calls `sign_transfer` for Alice's transfer ID.
5. `normalize_amount(500_000, Decimals { decimals: 18, origin_decimals: 24 })` = `500_000 / 1_000_000` = `0`.
6. `require!(0 > 0, ...)` panics with `InvalidAmountToTransfer`.
7. Alice's 500_000 base units are permanently locked in the bridge with no redemption path. [3](#0-2) [1](#0-0) [4](#0-3)

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

**File:** near/omni-bridge/src/lib.rs (L1834-1869)
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
```

**File:** near/omni-bridge/src/lib.rs (L2789-2792)
```rust
    fn normalize_amount(amount: u128, decimals: Decimals) -> u128 {
        let diff_decimals: u32 = (decimals.origin_decimals - decimals.decimals).into();
        amount / (10_u128.pow(diff_decimals))
    }
```
