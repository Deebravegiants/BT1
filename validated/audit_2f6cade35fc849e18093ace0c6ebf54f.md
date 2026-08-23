### Title
Missing aggregate size/count validation in `validate_deterministic_state_init` allows unbounded state-init payload per receipt - (File: runtime/runtime/src/action_validation.rs)

### Finding Description
`validate_deterministic_state_init` in `runtime/runtime/src/action_validation.rs` (lines 435-471) only validates the derived account id and, per key/value pair in `action.state_init.data()`, checks that each individual key/value stays under `limit_config.max_length_storage_key` / `max_length_storage_value`: [1](#0-0) 

There is no loop-level accumulation of total bytes or a count check on the number of `(key, value)` pairs in `action.state_init.data()`. The enclosing `validate_actions_with_mode` (lines 62-125) enforces `max_actions_per_receipt`, `max_deploy_actions_per_receipt`, and `max_total_prepaid_gas`, but none of these bound the total serialized size of a single `DeterministicStateInitAction`'s embedded state map: [2](#0-1) 

An attacker constructing a valid `DeterministicStateInitAction` (with `receiver_id` matching `derive_near_deterministic_account_id(&action.state_init)`) can include an arbitrarily large number of small key/value pairs, each individually compliant, with no code path in this function rejecting the aggregate.

### Impact Explanation
If no other layer (transaction/receipt total-size limit, borsh-serialization size cap, or network message size cap) independently bounds the serialized size of the whole action/receipt before or after this check runs, an attacker could produce a `DeterministicStateInitAction` receipt whose total payload significantly exceeds intended sizing assumptions (`max_receipt_size`), which per the referenced `congestion_control.rs`/`max_receipt_size.rs` logic feeds into congestion/bandwidth accounting and potentially state-witness size for the shard, risking resource-use amplification. I was not able to conclusively verify within this investigation whether a separate aggregate/serialized-size check for the whole receipt or the whole transaction (e.g., a general `max_transaction_size` check at transaction admission, or a receipt-serialized-size check invoked elsewhere such as in `verifier.rs`, which does reference `max_receipt_size` twice but whose exact enforcement point I could not fully inspect) already closes this gap before/after `validate_deterministic_state_init` runs.

### Likelihood Explanation
The precondition (crafting a `state_init` whose derived deterministic account id can be freely chosen by the attacker, since the id is deterministically derived from the payload itself rather than pre-existing) is met by design of the deterministic-account-id feature, so no privileged access is needed. Feasibility, however, hinges entirely on whether an independent aggregate size bound exists elsewhere in the transaction/receipt admission path; if a general transaction/receipt size limit already exists and is enforced prior to or independent of `validate_deterministic_state_init`, this specific gap has no exploitable effect.

### Recommendation
Add an aggregate check inside `validate_deterministic_state_init` that sums the total serialized size (and/or entry count) of `action.state_init.data()` and rejects the action if it exceeds a bound derived from `max_receipt_size` (or a dedicated new limit-config field), mirroring how `validate_access_key_permission` sums `total_number_of_bytes` across method names rather than only checking each individually.

### Proof of Concept
Add a unit test in `runtime/runtime/src/action_validation.rs`'s test module that builds a `DeterministicAccountStateInit`/`DeterministicAccountStateInitV1` with N entries (e.g., N = 100,000) each at `max_length_storage_key`/`max_length_storage_value`, derives the matching `receiver_id` via `derive_near_deterministic_account_id`, and calls `validate_deterministic_state_init` (or `validate_actions`) directly:
- Assert it currently returns `Ok(())` even though total serialized size vastly exceeds `limit_config.max_receipt_size` (or equivalent constant).
- After adding an aggregate-size check, assert the same input is rejected with a new `ActionsValidationError` variant once the total size crosses the intended limit, and add a fuzz/property test asserting no accepted `DeterministicStateInitAction` has `data()` total serialized size exceeding `max_receipt_size`.

### Citations

**File:** runtime/runtime/src/action_validation.rs (L62-122)
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
```

**File:** runtime/runtime/src/action_validation.rs (L451-468)
```rust
    // State init entries must not violate limits of individual state keys and values.
    for (key, value) in action.state_init.data() {
        if key.len() as u64 > limit_config.max_length_storage_key {
            return Err(ActionsValidationError::DeterministicStateInitKeyLengthExceeded {
                length: key.len() as u64,
                limit: limit_config.max_length_storage_key,
            }
            .into());
        }

        if value.len() as u64 > limit_config.max_length_storage_value {
            return Err(ActionsValidationError::DeterministicStateInitValueLengthExceeded {
                length: value.len() as u64,
                limit: limit_config.max_length_storage_value,
            }
            .into());
        }
    }
```
