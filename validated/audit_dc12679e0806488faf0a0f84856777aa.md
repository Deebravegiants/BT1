## Analysis

The TRST-M-10 pattern — computing a fee/size estimate from an *incomplete* payload, then having additional data appended afterward so the real object ends up larger than what was validated/charged — has a direct, currently-unfixed analog in `nearcore`'s receipt size validation.

### Root cause

When a new `ActionReceipt` is created, its size is validated once against `max_receipt_size`: [1](#0-0) 

This check runs in `ValidateReceiptMode::NewReceipt` at receipt-creation time. However, `output_data_receivers` — the list of accounts waiting on this receipt's return value, populated later via `promise_then`/`promise_return` chaining — can be appended to the `ActionReceipt` **after** this size check already passed, growing the receipt's actual borsh-serialized size beyond `max_receipt_size`.

The code openly documents this as a known, outstanding bug: [2](#0-1) 

The only mitigation in place is a defensive clamp applied purely for congestion/bandwidth bookkeeping when forwarding the (already oversized) receipt — it does not fix the validation gap itself: [3](#0-2) 

Two test-loop tests explicitly reproduce and label this as unfixed: [4](#0-3) [5](#0-4) 

This is tracked upstream as [nearcore issue #12606](https://github.com/near/nearcore/issues/12606).

### Why this matches the report's bug class

- MozBridge computed a LayerZero fee from a truncated payload representation (`abi.encode(_msgType)`), while the actual message sent included a much larger `Snapshot` struct appended afterward — an estimate-vs-actual-payload mismatch.
- Here, `nearcore` validates receipt size against `max_receipt_size` using the receipt as it exists at creation time, but `output_data_receivers` (and the resulting size increase) are attached afterward, so the enforced limit does not reflect the receipt's true final size — an identical estimate-vs-actual mismatch, just for a size/resource limit instead of a gas fee.

### Impact

Because the size check is bypassed, receipts can be created and stored (in the outgoing buffer, delayed receipt queue, or forwarded across shards) that exceed `max_receipt_size`. This is a resource-accounting bypass: it can inflate `ChunkStateWitness`/receipt-buffer sizes beyond the protocol's intended bound, undermining the very limit that exists to bound per-receipt state/network overhead, and it interacts with `ReceiptGroupsConfig`/bandwidth-scheduler logic (`core/store/src/trie/outgoing_metadata.rs:88-152`) whose invariant ("receipts in this group ... no larger than `max_receipt_size`") can be silently violated [6](#0-5) .

### What I could not fully verify

I could not trace the exact call sites in `runtime/runtime/src/function_call.rs` / `receipt_manager.rs` where `output_data_receivers` are appended relative to the `validate_receipt` call in `runtime/runtime/src/lib.rs`, because the tool budget ran out before the last `grep_search` results were returned. Based on the test names and code comments already found, the sequence (create/validate receipt → later attach `output_data_receivers` via `promise_return`) is described consistently across `verifier.rs`, `congestion_control.rs`, and the `max_receipt_size` test-loop tests, but a background Devin session with full file access would be needed to pin down the precise line ordering and confirm whether any protocol-version gate already closes this gap.

### Citations

**File:** runtime/runtime/src/verifier.rs (L527-541)
```rust
pub(crate) fn validate_receipt(
    limit_config: &LimitConfig,
    receipt: &Receipt,
    current_protocol_version: ProtocolVersion,
    mode: ValidateReceiptMode,
) -> Result<(), ReceiptValidationError> {
    if mode == ValidateReceiptMode::NewReceipt {
        let receipt_size: u64 =
            borsh::object_length(receipt).unwrap().try_into().expect("Can't convert usize to u64");
        if receipt_size > limit_config.max_receipt_size {
            return Err(ReceiptValidationError::ReceiptSizeExceeded {
                size: receipt_size,
                limit: limit_config.max_receipt_size,
            });
        }
```

**File:** runtime/runtime/src/verifier.rs (L573-586)
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ValidateReceiptMode {
    /// Used for validating new receipts that were just created.
    /// More strict than `OldReceipt` mode, which has to handle older receipts.
    NewReceipt,
    /// Used for validating older receipts that were saved in the state/received. Less strict than
    /// NewReceipt validation. Tolerates some receipts that wouldn't pass new validation. It has to
    /// be less strict because:
    /// 1) Older receipts might have been created before new validation rules.
    /// 2) There is a bug which allows to create receipts that are above the size limit. Runtime has
    ///    to handle them gracefully until the receipt size limit bug is fixed.
    ///    See https://github.com/near/nearcore/issues/12606 for details.
    ExistingReceipt,
}
```

**File:** runtime/runtime/src/congestion_control.rs (L403-427)
```rust
    fn try_forward(
        receipt: Receipt,
        gas: Gas,
        mut size: u64,
        shard: ShardId,
        outgoing_limit: &mut HashMap<ShardId, OutgoingLimit>,
        outgoing_receipts: &mut Vec<Receipt>,
        apply_state: &ApplyState,
        stats: &mut ReceiptSinkStats,
    ) -> Result<ReceiptForwarding, RuntimeError> {
        // There is a bug which allows to create receipts that are above the size limit. Receipts
        // above the size limit might not fit under the maximum outgoing size limit. Let's pretend
        // that all receipts are at most `max_receipt_size` to avoid receipts getting stuck.
        // See https://github.com/near/nearcore/issues/12606
        let max_receipt_size = apply_state.config.wasm_config.limit_config.max_receipt_size;
        if size > max_receipt_size {
            tracing::debug!(
                target: "runtime",
                receipt_id=?receipt.receipt_id(),
                size,
                max_receipt_size,
                "try_forward observed a receipt with size exceeding the size limit",
            );
            size = max_receipt_size;
        }
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L124-130)
```rust
// A function call will generate a new receipt. Size of this receipt will be equal to
// `max_receipt_size`, it'll pass validation, but then `output_data_receivers` will be modified and
// the receipt's size will go above max_receipt_size. The receipt should be rejected, but currently
// isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
// Runtime shouldn't die when it encounters a receipt with size above `max_receipt_size`.
#[test]
fn test_max_receipt_size_promise_return() {
```

**File:** test-loop-tests/src/tests/max_receipt_size.rs (L210-216)
```rust
/// Return a value that is as large as max_receipt_size. The value will be wrapped in a data receipt
/// and the data receipt will be bigger than max_receipt_size. The receipt should be rejected, but
/// currently isn't because of a bug (See https://github.com/near/nearcore/issues/12606)
/// Creates the following promise DAG:
/// A[self.return_large_value()] -then-> B[self.mark_test_completed()]
#[test]
fn test_max_receipt_size_value_return() {
```

**File:** core/store/src/trie/outgoing_metadata.rs (L96-104)
```rust
#[derive(Debug, PartialEq, Eq, BorshSerialize, BorshDeserialize, ProtocolSchema)]
pub struct ReceiptGroupV0 {
    /// Total size of receipts in this group.
    /// Should be no larger than `max_receipt_size`, otherwise the bandwidth
    /// scheduler will not be able to grant the bandwidth needed to send
    /// the receipts in this group.
    pub size: u64,
    /// Total gas of receipts in this group.
    pub gas: u128,
```
