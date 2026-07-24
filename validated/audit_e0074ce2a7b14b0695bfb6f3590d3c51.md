Looking at the full call chain: `init_transfer` → `sign_transfer` (NEAR) → `finalize_transfer` (Solana).

### Title
Permanent Fund Lock: No u64 Overflow Guard in `sign_transfer` Leaves NEAR-Initiated Transfers to Solana Unrecoverable — (`near/omni-bridge/src/lib.rs`, `solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs`)

---

### Summary

`sign_transfer` on NEAR normalizes the transfer amount to Solana's decimal precision but never validates that the result fits in `u64`. If `normalize_amount(raw_amount) > u64::MAX`, the MPC signs a payload with an overflowing amount, every Solana `finalize_transfer` call reverts with `AmountOverflow`, and NEAR has no cancel or refund path — permanently locking the user's tokens.

---

### Finding Description

**Step 1 — NEAR accepts and locks the transfer without a u64 bound check.**

`init_transfer_internal` burns or locks the user's tokens and stores the `TransferMessage` in `pending_transfers` with the raw `u128` amount. No upper-bound check against `u64::MAX` is performed at this stage. [1](#0-0) 

**Step 2 — `sign_transfer` normalizes the amount but only checks `> 0`, not `<= u64::MAX`.**

```
amount_to_transfer = raw_amount / 10^(origin_decimals − solana_decimals)
```

For a token where NEAR and Solana share the same decimal precision (e.g., both 9), the divisor is `10^0 = 1`, so `amount_to_transfer == raw_amount`. The only guard is `amount_to_transfer > 0`; there is no ceiling check. [2](#0-1) [3](#0-2) 

The overflowing value is then embedded verbatim into `TransferMessagePayload.amount` as `U128`: [4](#0-3) 

**Step 3 — Solana always reverts.**

Both `finalize_transfer` and `finalize_transfer_sol` perform `data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?`. If `data.amount > u64::MAX`, this conversion fails unconditionally and the transaction reverts before any state is mutated — including the nonce bitmap. [5](#0-4) [6](#0-5) 

Because Solana transactions are atomic, the nonce is never consumed. Every subsequent retry with the same signed payload reverts identically.

**Step 4 — NEAR has no recovery path.**

`remove_transfer_message` is only invoked inside `claim_fee_callback` (triggered by a successful Solana finalization proof) and `remove_transfer_message_without_refund` (triggered only by a storage-balance failure during `init_transfer_internal`). There is no public `cancel_transfer`, no expiry, and no DAO function to forcibly remove a stuck pending transfer and return the locked/burned tokens. [7](#0-6) [8](#0-7) 

Re-calling `sign_transfer` on the same `transfer_id` recomputes the same normalized amount from the unchanged stored message and produces an identical overflowing payload — there is no way to produce a valid Solana-side finalization.

---

### Impact Explanation

User tokens are burned or locked on NEAR at `init_transfer_internal` time. Because Solana finalization is the only path that removes the `pending_transfers` entry and (for native tokens) would trigger the Wormhole confirmation back to NEAR, the funds are permanently unrecoverable. This satisfies the **Critical — Irreversible fund lock** impact category.

---

### Likelihood Explanation

The overflow requires `normalize_amount(raw_amount) > u64::MAX ≈ 1.84 × 10^19`. For a token where NEAR and Solana share the same decimal precision (the normalization divisor is 1), this means transferring more than ~18.4 billion tokens (at 9 decimals). High-supply fungible tokens (meme tokens, governance tokens with large supplies) routinely exceed this threshold. The NEAR `ft_transfer_call` interface accepts any `U128` amount, so no client-side guard prevents submission. Likelihood is **Low-Medium** in practice but the impact when triggered is irreversible.

---

### Recommendation

1. **Add a u64 ceiling check in `sign_transfer`** immediately after computing `amount_to_transfer`:
   ```rust
   require!(
       amount_to_transfer <= u64::MAX as u128,
       BridgeError::AmountOverflow.as_ref()
   );
   ```
   This causes `sign_transfer` to revert before the MPC is invoked, leaving the transfer in `pending_transfers` in a state where the user can still update the fee or wait for a protocol-level recovery.

2. **Add a cancel/refund function** (DAO-gated or sender-gated) that removes a `pending_transfers` entry and returns locked/burned tokens to the sender, to handle any future stuck transfers.

3. **Optionally, add the same check in `init_transfer`** (after computing the normalized amount for the destination chain) to reject the transfer before tokens are locked.

---

### Proof of Concept

```rust
// Construct a FinalizeTransferPayload with amount = u64::MAX + 1
let payload = FinalizeTransferPayload {
    destination_nonce: 1,
    transfer_id: TransferId { origin_chain: ChainKind::Near, origin_nonce: 1 },
    token_address: some_mint,
    amount: u128::from(u64::MAX) + 1,   // overflows u64
    recipient: some_pubkey,
    fee_recipient: None,
    message: vec![],
};
// finalize_transfer always returns ProgramError::Custom(6010) = AmountOverflow
// nonce bitmap is never written → nonce remains reusable
// NEAR pending_transfers entry is never removed → tokens permanently locked
```

This matches the existing test at `solana/programs/bridge_token_factory/tests/mollusk/test_finalize_transfer.rs:261-270` which already confirms the revert, but no corresponding NEAR-side recovery test exists. [9](#0-8)

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

**File:** near/omni-bridge/src/lib.rs (L495-504)
```rust
        let transfer_payload = TransferMessagePayload {
            prefix: PayloadType::TransferMessage,
            destination_nonce: transfer_message.destination_nonce,
            transfer_id,
            token_address,
            amount: U128(amount_to_transfer),
            recipient: transfer_message.recipient,
            fee_recipient,
            message,
        };
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

**File:** near/omni-bridge/src/lib.rs (L2199-2216)
```rust
    fn remove_transfer_message(&mut self, transfer_id: TransferId) -> TransferMessage {
        let storage_usage = env::storage_usage();
        let transfer = self
            .pending_transfers
            .remove(&transfer_id)
            .map(storage::TransferMessageStorage::into_main)
            .near_expect(BridgeError::TransferNotExist);

        let refund =
            env::storage_byte_cost().saturating_mul((storage_usage - env::storage_usage()).into());

        if let Some(mut storage) = self.accounts_balances.get(&transfer.owner) {
            storage.available = storage.available.saturating_add(refund);
            self.accounts_balances.insert(&transfer.owner, &storage);
        }

        transfer.message
    }
```

**File:** near/omni-bridge/src/lib.rs (L2218-2229)
```rust
    fn remove_transfer_message_without_refund(
        &mut self,
        transfer_id: TransferId,
    ) -> TransferMessage {
        let transfer = self
            .pending_transfers
            .remove(&transfer_id)
            .map(storage::TransferMessageStorage::into_main)
            .near_expect(BridgeError::TransferNotExist);

        transfer.message
    }
```

**File:** near/omni-bridge/src/lib.rs (L2789-2792)
```rust
    fn normalize_amount(amount: u128, decimals: Decimals) -> u128 {
        let diff_decimals: u32 = (decimals.origin_decimals - decimals.decimals).into();
        amount / (10_u128.pow(diff_decimals))
    }
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs (L114-114)
```rust
                data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?,
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer_sol.rs (L88-88)
```rust
            data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?,
```

**File:** solana/programs/bridge_token_factory/tests/mollusk/test_finalize_transfer.rs (L260-270)
```rust
#[test]
fn finalize_transfer_amount_overflow() {
    let result = run_finalize_transfer(TestParams {
        amount: u128::from(u64::MAX) + 1,
        ..Default::default()
    });

    assert_eq!(
        result.program_result,
        ProgramResult::Failure(ProgramError::Custom(6010))
    );
```
