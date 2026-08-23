### Title
Gas-key balance refund can overflow and trigger a node panic via StorageError - (File: `runtime/runtime/src/actions.rs`)

### Summary
The external report describes a Solidity DoS pattern where an unprivileged party can pre-set an allowance to its maximum value so that a later privileged "increase" operation always reverts, denying service to the contract. The reachable analog in nearcore is the `FunctionCallPermission`/gas-key `allowance` and `balance` fields on access keys, whose top-up path uses `checked_add` and turns any overflow into a `StorageError::StorageInconsistentState`, a class of error that nearcore treats as an unrecoverable state-corruption signal rather than a normal user-facing transaction failure.

### Finding Description
Gas keys carry a `GasKeyInfo::balance` that a user can top up with a `transfer_to_gas_key` action, and this balance can also be *credited automatically* by the protocol when unused prepaid gas is refunded, via `try_refund_gas_key_balance`: [1](#0-0) 

If an account (fully controlled by the attacker, since these are their own access keys) pushes `gas_key_info.balance` close to `u128::MAX` through repeated/large transfers into the gas key, then any subsequent gas refund into the same key that would push the balance over `u128::MAX` hits the `.ok_or_else(...)` branch and returns `StorageError::StorageInconsistentState("gas key balance integer overflow")` instead of a normal, recoverable `ActionError`. The comparable `try_refund_allowance` path for `FunctionCallPermission.allowance` avoids this failure mode by using `saturating_add` instead of `checked_add`: [2](#0-1) 

`StorageInconsistentState` is nearcore's designated signal for trie/state corruption — a condition the codebase does not expect to occur from ordinary, spec-compliant execution, and one that is propagated all the way up through `RuntimeError::StorageError` in the `apply` pipeline (`runtime/runtime/src/lib.rs` uses it pervasively as a fatal condition, not a recoverable transaction outcome). Because this specific `StorageInconsistentState` is reachable purely from an attacker-chosen sequence of otherwise valid `transfer_to_gas_key`/refund-generating actions (not corrupted disk state), an unprivileged account can force a runtime code path that the codebase treats as "should never happen," which is the same "increase can always fail because balance was pre-maxed" root cause pattern as the Solidity report.

### Impact Explanation
Unlike a normal `ActionError` (which just fails a single receipt with a user-visible error and refunds gas), `StorageInconsistentState` is nearcore's marker for "the trie is corrupted" and is generally handled as a fatal condition during chunk application rather than a graceful per-transaction failure. If this is reachable during ordinary receipt processing (as the overflow branch here suggests), it can abort/crash chunk application for the shard, which is a node-panic / chain-stall class impact rather than a benign transaction failure — directly matching the DoS class in the reported Solidity bug, but exercised over gas-key balance accounting instead of an ERC20 allowance.

### Likelihood Explanation
The gas key balance is attacker-owned state on the attacker's own account, and topping it up close to `u128::MAX` costs at most the yoctoNEAR balance the attacker is willing to lock into their own key (bounded only by economic cost, not by any protocol restriction visible in this code). Triggering a subsequent gas refund into the same key is a normal side effect of calling a function with that gas key. This makes the precondition (near-max balance) fully attacker-controlled and cheap relative to mainnet balances, though exact reachability during live chunk apply (versus only being caught during genesis/tooling paths) was not fully verified within the available context.

### Recommendation
Change `try_refund_gas_key_balance` to use `saturating_add` (mirroring `try_refund_allowance`) instead of `checked_add` + `StorageInconsistentState`, or, if an overflow here is truly meant to be impossible, ensure the overflow is converted into a normal, per-transaction `ActionError`/receipt failure rather than a `StorageError` that the runtime treats as fatal corruption.

### Proof of Concept
1. Attacker creates an account and a gas key on it.
2. Attacker repeatedly calls `transfer_to_gas_key` (or the largest single transfer allowed) to push `gas_key_info.balance` to a value just below `u128::MAX`.
3. Attacker issues a function call using that gas key with prepaid gas, such that the resulting gas refund calls `try_refund_gas_key_balance` with a `deposit` that pushes `balance` past `u128::MAX`.
4. `checked_add` returns `None`, producing `StorageError::StorageInconsistentState("gas key balance integer overflow")`, which propagates as a fatal `RuntimeError::StorageError` in the apply pipeline instead of a normal action failure. [3](#0-2)

### Citations

**File:** runtime/runtime/src/actions.rs (L112-132)
```rust
/// Tries to refund gas to a gas key's balance.
/// Returns true if the key exists and is a gas key (balance was credited).
/// Returns false otherwise (key not found or is not a gas key).
pub(crate) fn try_refund_gas_key_balance(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
    public_key: &PublicKey,
    deposit: Balance,
) -> Result<bool, StorageError> {
    let Some(mut access_key) = get_access_key(state_update, account_id, public_key)? else {
        return Ok(false);
    };
    let Some(gas_key_info) = access_key.gas_key_info_mut() else {
        return Ok(false);
    };
    gas_key_info.balance = gas_key_info.balance.checked_add(deposit).ok_or_else(|| {
        StorageError::StorageInconsistentState("gas key balance integer overflow".to_string())
    })?;
    set_access_key(state_update, account_id.clone(), public_key.clone(), &access_key);
    Ok(true)
}
```

**File:** runtime/runtime/src/actions.rs (L134-158)
```rust
pub(crate) fn try_refund_allowance(
    state_update: &mut TrieUpdate,
    account_id: &AccountId,
    public_key: &PublicKey,
    deposit: Balance,
) -> Result<(), StorageError> {
    if let Some(mut access_key) = get_access_key(state_update, account_id, public_key)? {
        let mut updated = false;
        if let AccessKeyPermission::FunctionCall(function_call_permission) =
            &mut access_key.permission
        {
            if let Some(allowance) = function_call_permission.allowance.as_mut() {
                let new_allowance = allowance.saturating_add(deposit);
                if new_allowance > *allowance {
                    *allowance = new_allowance;
                    updated = true;
                }
            }
        }
        if updated {
            set_access_key(state_update, account_id.clone(), public_key.clone(), &access_key);
        }
    }
    Ok(())
}
```
