### Title
Dust Transfer Locks Tokens Permanently When `normalize_amount` Rounds to Zero - (`near/omni-bridge/src/lib.rs`)

### Summary

`init_transfer` accepts and locks user tokens without verifying that the normalized destination-chain amount is non-zero. When `normalize_amount(amount - fee)` rounds down to zero due to a large decimal difference between origin and destination chains, the tokens are permanently locked: `sign_transfer` will always revert with `InvalidAmountToTransfer`, and no cancel/refund path exists.

### Finding Description

The bug class from the external report is **arithmetic rounding to zero causing a critical state invariant to be violated**. In WooFi, `gamma = 0` meant price state was not updated. In Omni Bridge, the analog is `normalize_amount(amount - fee) = 0` meaning the transfer can never be completed, yet tokens are already locked.

`normalize_amount` performs floor division: [1](#0-0) 

When `origin_decimals > decimals` (e.g., NEAR with 24 decimals bridging to a chain with 6 decimals, `diff_decimals = 18`), any `amount - fee < 10^18` normalizes to zero.

`init_transfer` only validates `fee < amount`: [2](#0-1) 

It does **not** check whether `normalize_amount(amount - fee) > 0`. On success, `init_transfer_internal` locks/burns the tokens and returns `U128(0)` to the NEP-141 caller (no refund): [3](#0-2) 

Later, when a relayer calls `sign_transfer`, the zero-check fires and the call panics: [4](#0-3) 

The transfer message remains in `pending_transfers` with tokens locked, but `sign_transfer` will always revert for this transfer. `update_transfer_fee` only allows fees to increase (`fee.fee >= current_fee.fee`), so it cannot rescue the transfer: [5](#0-4) 

There is no cancel or user-initiated refund path for a successfully initiated transfer.

### Impact Explanation

**Critical — Irreversible fund lock.** User tokens are locked in the bridge contract with no mechanism to recover them. The `sign_transfer` call will always revert with `ERR_INVALID_AMOUNT_TO_TRANSFER`, making the transfer permanently unclaimable. This matches the allowed impact: *"Irreversible fund lock, frozen redemption path, or permanently unclaimable user or protocol value."*

### Likelihood Explanation

**Medium.** The condition requires a token with a large decimal difference between origin and destination chains (e.g., NEAR at 24 decimals → a 6-decimal destination, giving `diff_decimals = 18`). Any transfer of less than `10^18` base units (e.g., less than 1 NEAR in yoctoNEAR for a 24→6 decimal pair) triggers the bug. A user sending a "dust" amount or making a decimal mistake can trigger this accidentally. No privileged access is required — any user calling `ft_transfer_call` on the NEAR token contract is the entry point.

### Recommendation

Add a pre-flight check in `init_transfer` (before locking tokens) that verifies the normalized amount is non-zero. Specifically, look up the destination token's `Decimals` and assert:

```rust
let decimals = self.token_decimals.get(&token_address)
    .near_expect(BridgeError::TokenDecimalsNotFound);
let normalized = Self::normalize_amount(
    transfer_message.amount_without_fee().near_expect(BridgeError::InvalidFee),
    decimals,
);
require!(normalized > 0, BridgeError::InvalidAmountToTransfer.as_ref());
```

This mirrors the existing guard in `sign_transfer` but moves it to the point before tokens are locked, preventing the irreversible state.

### Proof of Concept

1. A NEAR-native token has `origin_decimals = 24`. Its deployed representation on a destination chain has `decimals = 6`. The stored `Decimals` struct is `{ decimals: 6, origin_decimals: 24 }`, so `diff_decimals = 18`.
2. User calls `ft_transfer_call` with `amount = 5 * 10^17` (0.5 yoctoNEAR-scale units), `fee = 0`, recipient on the 6-decimal chain.
3. `init_transfer` passes: `fee (0) < amount (5e17)` ✓. `init_transfer_internal` locks `5e17` tokens and returns `U128(0)`.
4. Relayer calls `sign_transfer`. `normalize_amount(5e17, {decimals:6, origin_decimals:24}) = 5e17 / 10^18 = 0`. The `require!(amount_to_transfer > 0)` panics.
5. Tokens remain locked forever. No cancel path exists. [6](#0-5) [4](#0-3) [7](#0-6)

### Citations

**File:** near/omni-bridge/src/lib.rs (L403-406)
```rust
                require!(
                    fee.fee >= current_fee.fee && fee.fee < transfer.message.amount,
                    BridgeError::InvalidFee.as_ref()
                );
```

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
