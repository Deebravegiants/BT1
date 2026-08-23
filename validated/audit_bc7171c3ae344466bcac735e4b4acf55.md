## Finding

### Title
Cross-shard receipt validation failure causes a node panic instead of graceful handling - (File: `chain/chain/src/runtime/mod.rs`)

### Summary
The MultiversX advisory describes a class of bug where an already-signed, cross-shard-forwarded message that fails an internal validity check on the *receiving* shard/processor was not handled gracefully, halting the chain. nearcore has a structurally analogous, currently-unmitigated path: when a cross-shard `Receipt` fails `validate_receipt` on the *destination* shard, the runtime returns `RuntimeError::ReceiptValidationError`, and the chain layer converts that into an explicit `panic!`, rather than a graceful `Error` like it does for `StorageError` or `InvalidTxError`.

### Finding Description
`Runtime::apply` validates every incoming (cross-shard) receipt before executing it, in `ValidateReceiptMode::ExistingReceipt` mode: [1](#0-0) 

`ExistingReceipt` mode is documented as intentionally *less strict* than `NewReceipt` mode precisely because "there is a bug which allows to create receipts that are above the size limit. Runtime has to handle them gracefully until the receipt size limit bug is fixed" (referencing nearcore issue #12606) — i.e. nearcore has already experienced, in production history, receipts that validated at creation time but would fail stricter validation later: [2](#0-1) 

Despite that mode relaxation, several checks in `validate_receipt`/`validate_action_receipt`/`validate_actions_with_mode` still run unconditionally in both `NewReceipt` and `ExistingReceipt` modes and are driven by the *current* `limit_config`/`current_protocol_version` at the time the receipt is processed on the destination shard — not the values in effect when the receipt was created on the source shard (e.g. `max_number_input_data_dependencies`, `max_actions_per_receipt`, `max_total_prepaid_gas`, `max_length_method_name`, `max_arguments_length`, the `PostQuantumSignatures` gate): [3](#0-2) [4](#0-3) 

If any `RuntimeError::ReceiptValidationError` is ever returned from `Runtime::apply` for a cross-shard incoming receipt (whether via a config/limit regression at an epoch boundary, a future regression re-introducing the #12606-style bug, or any other latent path that lets `NewReceipt` validation diverge from `ExistingReceipt` validation for a legitimately-forwarded receipt), the chain layer does not process it gracefully — it panics the node: [5](#0-4) 

This is explicitly marked `// TODO(#2152): process gracefully` in the code itself, i.e. the nearcore team is aware this is not yet handled the way `StorageError` and `InvalidTxError` are (which are converted into recoverable `Error` variants rather than panics).

### Impact Explanation
Because every validator/chunk-producer that tracks the destination shard runs the identical deterministic `Runtime::apply` code, a receipt that trips `ReceiptValidationError` on one node trips it on all nodes applying that chunk. The result is not a localized failure but a synchronized panic across all nodes processing that shard's chunk for that block — i.e. the shard (and, transitively, the chain, since other shards depend on chunks being produced/applied) stops making progress until an operator intervenes, mirroring the "metachain would have stopped notarizing blocks from shard chains" impact in the MultiversX advisory. This is a chain-stall risk, not a state-inconsistency or theft risk.

### Likelihood Explanation
Under the current protocol-limit configuration this is not trivially triggerable by an ordinary user today, because the code comments indicate nearcore has already tightened `NewReceipt` validation to be a superset of `ExistingReceipt` validation and closed the previously-known #12606 size-limit gap. However, the panic path itself remains live and un-guarded (per the open `#2152` TODO), and it depends on an implicit, undocumented invariant — "no receipt that validates at creation time can ever later fail `ExistingReceipt` validation at its destination shard" — that is not enforced by any structural guarantee (e.g. protocol-config decreases, or config divergence around an epoch boundary while a receipt is in flight, could break it). This makes it a latent, currently-low-but-nonzero-likelihood chain-halt bug rather than a fully theoretical one.

### Recommendation
Convert `RuntimeError::ReceiptValidationError` on the incoming-receipt path into a recoverable, non-panicking error (e.g. treat it the way `StorageInconsistentState` is already treated for delayed receipts — as a hard protocol/logic error that produces a bounded outcome rather than a node crash), and resolve the outstanding `#2152` TODO by auditing all `RuntimeError` variants converted at `chain/chain/src/runtime/mod.rs:360-373` for panics that could be reachable from state/data that isn't fully protocol-invariant across shard boundaries.

### Proof of Concept
Not independently reproducible from the indexed source alone (no dedicated test triggers `RuntimeError::ReceiptValidationError` for a legitimately-forwarded cross-shard receipt); the analysis is based on tracing the exact code path from `process_incoming_receipts` → `validate_receipt` → `RuntimeError::ReceiptValidationError` → the `panic!` in `chain/chain/src/runtime/mod.rs:371`, combined with the codebase's own comments acknowledging a historical instance of this exact class of bug (issue #12606) and an open tracking issue (#2152) for the panic being non-graceful. [6](#0-5)

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

**File:** runtime/runtime/src/verifier.rs (L527-571)
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
    }

    // We retain these checks here as to maintain backwards compatibility
    // with AccountId validation since we illegally parse an AccountId
    // in near-vm-logic/logic.rs#fn(VMLogic::read_and_parse_account_id)
    AccountId::validate(receipt.predecessor_id().as_ref()).map_err(|_| {
        ReceiptValidationError::InvalidPredecessorId {
            account_id: receipt.predecessor_id().to_string(),
        }
    })?;
    AccountId::validate(receipt.receiver_id().as_ref()).map_err(|_| {
        ReceiptValidationError::InvalidReceiverId { account_id: receipt.receiver_id().to_string() }
    })?;

    match receipt.versioned_receipt() {
        VersionedReceiptEnum::Action(action_receipt)
        | VersionedReceiptEnum::PromiseYield(action_receipt) => validate_action_receipt(
            limit_config,
            action_receipt,
            receipt.receiver_id(),
            current_protocol_version,
            mode,
        ),
        VersionedReceiptEnum::Data(data_receipt)
        | VersionedReceiptEnum::PromiseResume(data_receipt) => {
            validate_data_receipt(limit_config, &data_receipt)
        }
        VersionedReceiptEnum::GlobalContractDistribution(_) => Ok(()), // Distribution receipt can't be issued without a valid contract
    }
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

**File:** runtime/runtime/src/action_validation.rs (L62-125)
```rust
pub(crate) fn validate_actions_with_mode(
    limit_config: &LimitConfig,
    actions: &[Action],
    receiver: &AccountId,
    current_protocol_version: ProtocolVersion,
    mode: ValidateReceiptMode,
) -> Result<(), ActionsValidationError> {
    if actions.len() as u64 > limit_config.max_actions_per_receipt {
        return Err(ActionsValidationError::TotalNumberOfActionsExceeded {
            total_number_of_actions: actions.len() as u64,
            limit: limit_config.max_actions_per_receipt,
        });
    }

    // Centralized post-quantum gate. Mirrors the tx-admission gate in
    // `check_valid_for_config`, and is load-bearing for actions emitted by
    // contracts via host functions: those actions create new receipts that
    // never go through tx admission, so on a pre-feature protocol they must
    // be rejected here. The exhaustive match in
    // `Action::post_quantum_signatures_required` (including the recursive
    // walk into `Delegate`) forces every future action variant to make an
    // explicit decision at compile time.
    if !ProtocolFeature::PostQuantumSignatures.enabled(current_protocol_version)
        && actions.iter().any(Action::post_quantum_signatures_required)
    {
        return Err(ActionsValidationError::UnsupportedProtocolFeature {
            protocol_feature: "PostQuantumSignatures".to_owned(),
            version: current_protocol_version,
        });
    }

    if mode == ValidateReceiptMode::NewReceipt {
        validate_number_of_deploy_actions(actions, limit_config.max_deploy_actions_per_receipt)?;
    }

    let mut found_delegate_action = false;
    let mut iter = actions.iter().peekable();
    while let Some(action) = iter.next() {
        if let Action::DeleteAccount(_) = action {
            if iter.peek().is_some() {
                return Err(ActionsValidationError::DeleteActionMustBeFinal);
            }
        } else {
            if let Action::Delegate(_) | Action::DelegateV2(_) = action {
                if found_delegate_action {
                    return Err(ActionsValidationError::DelegateActionMustBeOnlyOne);
                }
                found_delegate_action = true;
            }
        }
        validate_action_with_mode(limit_config, action, receiver, current_protocol_version, mode)?;
    }

    let total_prepaid_gas =
        total_prepaid_gas(actions).map_err(|_| ActionsValidationError::IntegerOverflow)?;
    if total_prepaid_gas > limit_config.max_total_prepaid_gas {
        return Err(ActionsValidationError::TotalPrepaidGasExceeded {
            total_prepaid_gas,
            limit: limit_config.max_total_prepaid_gas,
        });
    }

    Ok(())
}
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
