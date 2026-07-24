### Title
Tokens Permanently Locked When `normalize_amount` Truncates Transfer Amount to Zero — (`near/omni-bridge/src/lib.rs`)

### Summary

`init_transfer_internal` locks or burns user tokens before validating that the decimal-normalized transfer amount is non-zero. When `normalize_amount(amount - fee, decimals)` truncates to `0` due to integer floor division, the subsequent `sign_transfer` call permanently reverts, leaving the user's tokens irreversibly locked with no cancellation path.

### Finding Description

The NEAR bridge normalizes token amounts when crossing chains with different decimal precisions. The normalization divides by `10^(origin_decimals - decimals)`: [1](#0-0) 

This is applied in `sign_transfer` to compute the amount that will be sent to the destination chain: [2](#0-1) 

If the result is zero, `sign_transfer` reverts: [3](#0-2) 

The critical flaw is that token locking/burning happens **before** this check, inside `init_transfer_internal`: [4](#0-3) 

The `init_transfer` entry path (via `ft_on_transfer`) only validates `fee < amount`: [5](#0-4) 

There is no pre-lock check that `normalize_amount(amount - fee, decimals) > 0`. Once `init_transfer_internal` completes, the transfer message is stored in `pending_transfers` and the tokens are gone. There is no user-callable cancel or refund function in the contract.

### Impact Explanation

**Critical — Irreversible fund lock.** Any user who initiates a transfer with an amount smaller than the normalization divisor (`10^(origin_decimals - decimals)`) will have their tokens permanently locked. `sign_transfer` will always revert for that transfer ID, and no other code path releases the locked tokens back to the user.

Example: A NEAR-native token with 24 decimals bridging to an EVM token registered with 6 decimals produces `diff_decimals = 18`, divisor = `10^18`. Any transfer of fewer than `10^18` base units (i.e., less than 1 full token) normalizes to 0 and is permanently stuck.

The `Decimals` struct confirms both values are stored per token: [6](#0-5) 

And registered via `add_token` / `bind_token_callback`: [7](#0-6) 

### Likelihood Explanation

**Medium.** Any token pair where `origin_decimals > decimals` (e.g., 24-decimal NEAR tokens bridging to 6-decimal EVM tokens, a standard configuration) is affected. A user sending a sub-unit amount — which is a normal, unprivileged action through the public `ft_on_transfer` entry point — triggers the lock. No privileged access or external dependency compromise is required.

### Recommendation

Add a pre-lock validation in `init_transfer` (before calling `init_transfer_internal`) that checks the normalized amount is non-zero for the target chain's registered decimals. Alternatively, add a user-callable `cancel_transfer` function that allows the transfer owner to reclaim locked tokens for transfers that have never been signed.

### Proof of Concept

1. Token `tok.near` is registered with `origin_decimals = 24`, `decimals = 6` (bridging to EVM). Divisor = `10^18`.
2. User calls `tok.near::ft_transfer_call(bridge, amount=500_000_000_000_000_000, msg=...)` (0.5 tokens in 24-decimal units, a valid non-zero amount satisfying `fee < amount`).
3. `init_transfer` passes the `fee < amount` check and calls `init_transfer_internal`.
4. `init_transfer_internal` locks 500_000_000_000_000_000 base units and stores the transfer message.
5. Relayer calls `sign_transfer(transfer_id, ...)`.
6. `normalize_amount(500_000_000_000_000_000, {origin_decimals:24, decimals:6})` = `500_000_000_000_000_000 / 10^18` = **0**.
7. `require!(amount_to_transfer > 0, ...)` panics. [3](#0-2) 
8. No signature is ever produced. The transfer message stays in `pending_transfers` forever. The 500_000_000_000_000_000 base units are permanently locked with no recovery path.

### Citations

**File:** near/omni-bridge/src/lib.rs (L486-489)
```rust
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

**File:** near/omni-bridge/src/lib.rs (L2729-2740)
```rust
        require!(
            self.token_decimals
                .insert(
                    token_address,
                    &Decimals {
                        decimals,
                        origin_decimals,
                    }
                )
                .is_none(),
            BridgeError::TokenExists.as_ref()
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

**File:** near/omni-bridge/src/storage.rs (L131-136)
```rust
#[near(serializers=[borsh, json])]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Decimals {
    pub decimals: u8,
    pub origin_decimals: u8,
}
```
