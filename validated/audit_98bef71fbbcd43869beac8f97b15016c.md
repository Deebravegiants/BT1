### Title
Off-by-One in `DelegateAction` Expiry Check Allows Execution at `max_block_height` - (File: `runtime/runtime/src/actions.rs`)

### Summary

The `apply_delegate_action` function in `runtime/runtime/src/actions.rs` uses a strict `>` comparison to check whether a `DelegateAction` has expired, but the protocol specification and field documentation require a `>=` check. This allows a relayer to execute a delegated action at exactly `block_height == max_block_height`, one block past the user's intended expiry.

### Finding Description

The `DelegateAction` struct carries a `max_block_height` field documented as:

> "The maximal height of the block in the blockchain **below which** the given DelegateAction is valid."

The protocol spec in `docs/RuntimeSpec/Actions.md` states the action should fail with `DelegateActionExpired` when:

> "the current block is **equal or greater than** `max_block_height`"

However, the enforcement in `apply_delegate_action` uses strict greater-than:

```rust
if apply_state.block_height > delegate_action.max_block_height() {
    result.result = Err(ActionErrorKind::DelegateActionExpired.into());
    return Ok(());
}
```

This means when `block_height == max_block_height`, the condition is `false` and the action proceeds — the opposite of what the spec requires. The action should be rejected at `block_height >= max_block_height`, but is only rejected at `block_height > max_block_height`.

The existing test `test_delegate_action_max_height` only tests `max_block_height + 1`, leaving the boundary case untested and the bug undetected:

```rust
// Setup current block as higher than max_block_height. Must fail.
let apply_state = create_apply_state(signed_delegate_action.delegate_action.max_block_height + 1);
```

### Impact Explanation

A relayer (an unprivileged account that submits meta-transactions on behalf of users) can deliberately hold a signed `DelegateAction` and submit it at exactly `block_height == max_block_height`. The action executes — performing balance transfers, contract calls, or other state mutations — at a block height the signer explicitly intended to be the expiry boundary. The corrupted protocol value is the execution outcome (account balance, contract state, nonce) of the `DelegateAction` receipt that should have been rejected.

### Likelihood Explanation

Block heights are publicly observable and predictable. A relayer can trivially time submission to land at exactly `max_block_height`. No special privileges are required — any account acting as a relayer can exploit this. The user has no recourse once the action is submitted at the boundary block.

### Recommendation

Change the comparison from strict greater-than to greater-than-or-equal:

```rust
// Before (incorrect):
if apply_state.block_height > delegate_action.max_block_height() {

// After (correct):
if apply_state.block_height >= delegate_action.max_block_height() {
```

Add a test case for the boundary condition `block_height == max_block_height` to `test_delegate_action_max_height`.

### Proof of Concept

The root cause is at: [1](#0-0) 

The field's own documentation states the action is valid only for blocks **below** `max_block_height`: [2](#0-1) 

The protocol spec confirms expiry triggers at `>=`: [3](#0-2) 

The existing test only covers `max_block_height + 1`, missing the boundary: [4](#0-3)

### Citations

**File:** runtime/runtime/src/actions.rs (L435-438)
```rust
    if apply_state.block_height > delegate_action.max_block_height() {
        result.result = Err(ActionErrorKind::DelegateActionExpired.into());
        return Ok(());
    }
```

**File:** runtime/runtime/src/actions.rs (L1358-1361)
```rust
        // Setup current block as higher than max_block_height. Must fail.
        let apply_state =
            create_apply_state(signed_delegate_action.delegate_action.max_block_height + 1);
        let mut state_update = setup_account(&sender_id, &sender_pub_key, &access_key);
```

**File:** core/primitives/src/action/delegate.rs (L60-61)
```rust
    /// The maximal height of the block in the blockchain below which the given DelegateAction is valid.
    pub max_block_height: BlockHeight,
```

**File:** docs/RuntimeSpec/Actions.md (L402-407)
```markdown
- If the current block is equal or greater than `max_block_height`

```rust
/// Delegate action has expired
DelegateActionExpired
```
```
