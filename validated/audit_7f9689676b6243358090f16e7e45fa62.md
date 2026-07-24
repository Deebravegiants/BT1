### Title
Replay of Finalized Transfer After Recipient-Triggered Refund Path Removes `finalised_transfers` Entry — (`near/omni-bridge/src/lib.rs`)

### Summary

`fin_transfer_send_tokens_callback` calls `remove_fin_transfer` on the failure path, which removes the `TransferId` from `finalised_transfers`. This allows a relayer to re-submit the identical proof and settle the same cross-chain transfer a second time, producing an unbacked double-mint.

---

### Finding Description

The callback at line 1697 handles the result of `ft_transfer_call` to the recipient. When `is_refund_required` returns `true`, the code burns the minted tokens and then **removes the deduplication entry**: [1](#0-0) 

```rust
if Self::is_refund_required(is_ft_transfer_call) {
    self.burn_tokens_if_needed(token.clone(), U128(...));
    self.revert_lock_actions(&lock_actions);
    self.remove_fin_transfer(&transfer_message.get_transfer_id(), storage_owner);
    // logs FailedFinTransferEvent
}
```

`is_refund_required` returns `true` when the `ft_transfer_call` promise result is `0` — meaning the recipient's `ft_on_transfer` returned the full amount (requesting a full refund) or panicked: [2](#0-1) 

```rust
fn is_refund_required(is_ft_transfer_call: bool) -> bool {
    if is_ft_transfer_call {
        match env::promise_result_checked(0, MAX_FT_TRANSFER_CALL_RESULT) {
            Ok(value) => {
                if let Ok(amount) = near_sdk::serde_json::from_slice::<U128>(&value) {
                    amount.0 == 0   // <-- true when recipient returned full refund
                } else { false }
```

**Correction to the question's premise:** The trigger is NOT "returning 0 from `ft_on_transfer`". In NEP-141, `ft_on_transfer` returns the amount to *refund* (unused tokens). Returning `0` means all tokens were used (no refund), which makes `ft_transfer_call` return the full amount → `is_refund_required = false`. To trigger the refund path, the recipient must return the **full amount** from `ft_on_transfer` (or panic), causing `ft_transfer_call` to resolve to `0`.

After `remove_fin_transfer` clears the `TransferId` from `finalised_transfers`: [3](#0-2) 

```rust
pub finalised_transfers: LookupSet<TransferId>,
```

…the same proof can be re-submitted. `add_fin_transfer` (called inside `process_fin_transfer_to_near`) will succeed because the entry no longer exists, and a second settlement is processed.

---

### Impact Explanation

- **First attempt:** tokens minted → recipient rejects (returns full amount) → tokens burned → `finalised_transfers` entry deleted.
- **Second attempt (same proof):** `add_fin_transfer` succeeds → tokens minted again → recipient accepts → attacker holds tokens backed by a single source-chain lock event.

Net result: one source-chain lock event produces two NEAR-side mint events. This is an unbacked supply inflation / double-mint.

---

### Likelihood Explanation

- The attacker only needs to control the recipient address on NEAR (a contract they deploy).
- The `msg` field in the original transfer must be non-empty (so `ft_transfer_call` is used instead of `ft_transfer`). The sender controls `msg` at initiation time on the source chain.
- No privileged role, key, or MPC compromise is required.
- Any relayer (including the attacker acting as relayer, or a colluding relayer) can re-submit the proof after the entry is cleared.

---

### Recommendation

**Do not remove the `TransferId` from `finalised_transfers` on the failure path.** The deduplication invariant must be permanent: once a proof is accepted and `add_fin_transfer` succeeds, the entry must remain in `finalised_transfers` regardless of the downstream token transfer outcome.

If a refund/retry mechanism is needed, it should be handled separately (e.g., a dedicated retry queue or a flag on the entry) without ever clearing the finalization record.

---

### Proof of Concept

1. Deploy a NEAR contract `MaliciousRecipient` whose `ft_on_transfer` returns the full `amount` (requesting full refund).
2. On the source chain, initiate a transfer with `recipient = MaliciousRecipient` and a non-empty `msg`.
3. Submit `fin_transfer(proof)` on NEAR:
   - `add_fin_transfer` inserts `TransferId` into `finalised_transfers`.
   - `ft_transfer_call` is issued; `MaliciousRecipient.ft_on_transfer` returns `amount`.
   - `fin_transfer_send_tokens_callback` sees `is_refund_required = true`.
   - `burn_tokens_if_needed` burns the minted tokens.
   - `remove_fin_transfer` **deletes** `TransferId` from `finalised_transfers`.
4. Re-submit the identical `fin_transfer(proof)`:
   - `add_fin_transfer` succeeds (entry was removed).
   - Tokens are minted a second time to a legitimate recipient.
5. Assert: the legitimate recipient holds tokens; the source chain has only one locked event. Double-mint confirmed.

### Citations

**File:** near/omni-bridge/src/lib.rs (L224-228)
```rust
pub struct Contract {
    pub factories: LookupMap<ChainKind, OmniAddress>,
    pub pending_transfers: LookupMap<TransferId, TransferMessageStorage>,
    pub finalised_transfers: LookupSet<TransferId>,
    pub finalised_utxo_transfers: LookupSet<UnifiedTransferId>,
```

**File:** near/omni-bridge/src/lib.rs (L1707-1723)
```rust
        if Self::is_refund_required(is_ft_transfer_call) {
            self.burn_tokens_if_needed(
                token.clone(),
                U128(
                    transfer_message
                        .amount_without_fee()
                        .near_expect(BridgeError::InvalidFee),
                ),
            );

            self.revert_lock_actions(&lock_actions);

            self.remove_fin_transfer(&transfer_message.get_transfer_id(), storage_owner);

            env::log_str(
                &OmniBridgeEvent::FailedFinTransferEvent { transfer_message }.to_log_string(),
            );
```

**File:** near/omni-bridge/src/lib.rs (L1789-1800)
```rust
    fn is_refund_required(is_ft_transfer_call: bool) -> bool {
        if is_ft_transfer_call {
            match env::promise_result_checked(0, MAX_FT_TRANSFER_CALL_RESULT) {
                Ok(value) => {
                    if let Ok(amount) = near_sdk::serde_json::from_slice::<U128>(&value) {
                        // Normal case: refund if the used token amount is zero
                        // The amount can be zero if the `ft_on_transfer` in the receiver contract returns an amount instead of `0`, or if it panics.
                        amount.0 == 0
                    } else {
                        // Unexpected case: don't refund
                        false
                    }
```
