Based on my investigation, this is a valid analog.

### Title
Malformed incoming cross-shard receipt causes node panic via `RuntimeError::ReceiptValidationError` - (File: `chain/chain/src/runtime/mod.rs`)

### Summary
Like the Indy TAA bug where a malformed client transaction crashed the primary and forced a view change, nearcore has a code path where a receipt that fails `validate_receipt` during incoming-receipt processing is converted into `RuntimeError::ReceiptValidationError`, which is then turned into a hard `panic!` in `Chain::apply_transactions`-adjacent runtime adapter code, rather than being handled gracefully.

### Finding Description
`validate_receipt` (`runtime/runtime/src/verifier.rs:527-571`) is invoked from `process_incoming_receipts` (`runtime/runtime/src/lib.rs:2591-2597`) in `ValidateReceiptMode::ExistingReceipt` mode on every incoming cross-shard receipt before it is executed or delayed. If validation fails, the error is mapped directly to `RuntimeError::ReceiptValidationError` and returned up the call stack: [1](#0-0) 

That `RuntimeError` propagates out of `Runtime::apply` and is handled in the chain runtime adapter, where it is explicitly turned into an unconditional panic (marked `TODO(#2152): process gracefully`): [2](#0-1) 

Receipts reaching `process_incoming_receipts` originate from action receipts created by contract execution (e.g., via `FunctionCall`, `Transfer`, cross-contract calls) that were emitted on another shard and are validated with `ValidateReceiptMode::NewReceipt` at creation time (`runtime/runtime/src/lib.rs:914-925`), but that "new-receipt" validation is not identical to `ExistingReceipt`-mode re-validation performed on the receiving shard — the code comment explicitly acknowledges a historical bug class here: `ValidateReceiptMode::ExistingReceipt` exists specifically because "there is a bug which allows to create receipts that are above the size limit... Runtime has to handle them gracefully until the receipt size limit bug is fixed" (referencing `near/nearcore#12606`): [3](#0-2) 

This documents that a mismatch between creation-time and receive-time validation has occurred before in this exact code path, and the current handling for *any* future divergence (not just size) is a `panic!` on every node that must apply the chunk containing that incoming receipt — not just a "primary" but the entire validator set for that shard, since nearcore requires all validators tracking the shard to independently re-execute the state transition.

### Impact Explanation
Because `Runtime::apply` is called by every validator/RPC node responsible for applying a shard's chunk, a single malformed receipt that passes creation-time `NewReceipt` validation but fails `ExistingReceipt` validation on receipt would deterministically panic every node applying that chunk simultaneously. This is a chain-wide liveness bug: unlike the Indy case (crash a single primary → view change), in nearcore this could crash all block/chunk producers and validators tracking the affected shard at the same block height, causing a chain halt (analogous to, but more severe than, "repeated rapid view changes bringing down the network"). This matches the required impact category "node panic ... chain stall."

### Likelihood Explanation
Reaching this path requires constructing a receipt that satisfies `NewReceipt`-mode validation at creation (so it is allowed to be emitted and forwarded cross-shard) but fails `ExistingReceipt`-mode validation on the receiving shard. The codebase's own comment confirms such a divergence has existed in production before (`near/nearcore#12606`, receipt-size-limit bug), meaning the two validation modes are not provably equivalent and future protocol changes affecting `validate_action_receipt`/`validate_data_receipt` risk reintroducing such a gap. The trigger is a normal user-submitted transaction/contract call (no validator or malicious-peer privileges required) whose contract logic constructs a receipt at the edge of a validation-affecting parameter (size, `input_data_ids` count, refund-to account id, action limits) under specific protocol-version/config combinations. This is not proven to be currently exploitable (I could not identify a concrete present-day gap between the two validation modes), so likelihood is speculative but structurally plausible given the documented precedent and the explicit `TODO(#2152): process gracefully` marking this as a known-accepted risk area.

### Recommendation
Replace the `panic!` on `RuntimeError::ReceiptValidationError` (and `RuntimeError::UnexpectedIntegerOverflow`) in `chain/chain/src/runtime/mod.rs:366-371` with graceful error handling that fails only the affected chunk/receipt (e.g., treating it like `StorageInconsistentState` or rejecting/quarantining the receipt) rather than aborting the node process. Additionally, audit `validate_action_receipt`/`validate_data_receipt` to ensure `NewReceipt` mode is a strict superset of `ExistingReceipt` mode checks (or vice versa, so nothing can pass creation-time checks yet fail receipt-time checks), closing the class of bug referenced by `near/nearcore#12606`.

### Proof of Concept
Not reproduced directly; no concrete input was found in this pass that currently differs between `ValidateReceiptMode::NewReceipt` and `ValidateReceiptMode::ExistingReceipt` for a receipt that would successfully be created and forwarded cross-shard. The `test_max_receipt_size` and `test_max_receipt_size_yield_resume` tests in `test-loop-tests/src/tests/max_receipt_size.rs` confirm that oversized receipts are currently caught at creation time (`NewReceiptValidationError`), so the previously-known instance of this divergence (`near/nearcore#12606`) appears fixed on this version. The panic call site itself, however, remains live and unguarded, representing residual risk should any future validation-mode asymmetry be introduced (e.g., via new action types, protocol-version-gated checks, or the `refund_to` / `input_data_ids` checks added in `validate_action_receipt`).

### Citations

**File:** runtime/runtime/src/lib.rs (L2588-2597)
```rust
        for receipt in processing_state.incoming_receipts {
            // Validating new incoming no matter whether we have available gas or not. We don't
            // want to store invalid receipts in state as delayed.
            validate_receipt(
                &processing_state.apply_state.config.wasm_config.limit_config,
                receipt,
                protocol_version,
                ValidateReceiptMode::ExistingReceipt,
            )
            .map_err(RuntimeError::ReceiptValidationError)?;
```

**File:** chain/chain/src/runtime/mod.rs (L360-373)
```rust
            .map_err(|e| match e {
                RuntimeError::InvalidTxError(err) => {
                    tracing::warn!(?err, "invalid tx");
                    Error::InvalidTransactions
                }
                // TODO(#2152): process gracefully
                RuntimeError::UnexpectedIntegerOverflow(reason) => {
                    panic!("RuntimeError::UnexpectedIntegerOverflow {reason}")
                }
                RuntimeError::StorageError(e) => Error::StorageError(e),
                // TODO(#2152): process gracefully
                RuntimeError::ReceiptValidationError(e) => panic!("{}", e),
                RuntimeError::ValidatorError(e) => e.into(),
            })?;
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
