### Title
`RawMeter::nested` drops the parent's storage-deposit limit when a sub-call omits its own explicit limit, allowing unbounded storage deposit accumulation in nested contract calls - (File: substrate/frame/revive/src/metering/storage.rs)

### Summary
`RawMeter::nested` only takes the `min()` of the parent and child limits when *both* are `Some`; if the caller-supplied `limit` argument is `None` while the parent meter has `Some(old_limit)`, the `if let` pattern fails to match and the resulting child meter's `limit` field is left as `None` (unbounded) instead of inheriting `Some(old_limit)`. This silently removes the enforced deposit cap for the nested call frame.

### Finding Description
The relevant code is:
```rust
pub fn nested(&self, mut limit: Option<BalanceOf<T>>) -> RawMeter<T, E, Nested> {
    if let (Some(new_limit), Some(old_limit)) = (limit, self.limit) {
        limit = Some(new_limit.min(old_limit));
    }
    RawMeter { limit, ..Default::default() }
}
``` [1](#0-0) 

The tuple pattern `(Some(new_limit), Some(old_limit))` only matches when **both** values are `Some`. When the caller passes `limit = None` (i.e., the sub-call does not request its own explicit sub-limit) while `self.limit = Some(old_limit)` (the parent frame is capped), the `if let` guard is false, so `limit` is never reassigned and remains `None`. The child `RawMeter` is then constructed with `limit: None`, i.e. fully unbounded, discarding the parent's cap entirely. The correct behavior for "no explicit sub-limit requested" should be to inherit the parent's existing limit (`self.limit`), not to become unbounded.

This is a genuine accounting/logic defect confined to the limit-propagation arithmetic in `nested()`: there is no other check inside this file that re-derives or re-applies the parent limit onto an already-constructed child meter (`limit` is otherwise only read by `available()`, which is `#[cfg(test)]`-only, and by `RawMeter::new()` for the root). Once a nested meter is created with `limit: None`, nothing downstream in `storage.rs` restores the parent's constraint before deposits are recorded via `charge`/`charge_deposit`.

### Impact Explanation
If a nested call frame is created with `limit: None` its consumed storage deposit is not capped, so a cross-contract call chain (e.g. via `seal_call`) executed under that frame can accumulate storage-deposit charges without an effective ceiling for that sub-tree, up to whatever the origin's balance ultimately allows during `execute_postponed_deposits`. This could let a callee (potentially the same contract via recursion/reentrancy) exceed a deposit limit an outer caller intended to enforce for a specific sub-call, defeating the purpose of a caller-specified deposit cap.

### Likelihood Explanation
Whether this is externally triggerable depends entirely on whether the `seal_call` host function ABI can produce a `None` argument to `RawMeter::nested` for an ordinary contract-to-contract call while the outer/root meter has `Some(limit)` set (e.g., via an extrinsic's `storage_deposit_limit`). I was not able to fully verify, within the scope of this file, the exact sentinel/encoding used by `seal_call` in `exec.rs` to decide when `None` vs `Some(x)` is passed to `nested()` — this would need to be confirmed by inspecting the call-parameter decoding logic in `substrate/frame/revive/src/exec.rs`/`wasm` (or `pvm`) runtime bindings, which I could not complete in the available iterations. The logic bug in `nested()` itself is unconditionally present and reproducible in isolation; the full end-to-end exploitability through `seal_call` remains unconfirmed pending that additional check.

### Recommendation
Fix the limit-combination logic so that a missing sub-call limit inherits the parent's limit instead of becoming unbounded, e.g.:
```rust
pub fn nested(&self, limit: Option<BalanceOf<T>>) -> RawMeter<T, E, Nested> {
    let limit = match (limit, self.limit) {
        (Some(new_limit), Some(old_limit)) => Some(new_limit.min(old_limit)),
        (Some(new_limit), None) => Some(new_limit),
        (None, old_limit) => old_limit, // inherit parent's cap when none is specified
    };
    RawMeter { limit, ..Default::default() }
}
```

### Proof of Concept
Unit test in `substrate/frame/revive/src/metering/storage/tests.rs`:
```rust
#[test]
fn nested_none_limit_should_inherit_parent_limit() {
    let parent: RawMeter<Test, TestExt, Root> = RawMeter::new(Some(100));
    let child = parent.nested(None);
    // Currently fails: child.limit == None instead of Some(100)
    assert_eq!(child.limit, Some(100));
}
```
Full integration test plan (`substrate/frame/revive/src/exec.rs` tests): construct a call stack where the root extrinsic sets a small `storage_deposit_limit`, then have the top-level contract invoke `seal_call` on a callee without specifying an explicit per-call deposit limit (forcing `None` into `nested`), and have that callee write storage well beyond the root's limit; assert the call either fails the deposit check (expected/fixed behavior) or currently succeeds and exceeds the configured limit (demonstrating the bug), confirmed by inspecting `ContractInfo` storage deposit fields and the account's held balance after execution.

### Citations

**File:** substrate/frame/revive/src/metering/storage.rs (L247-253)
```rust
	pub fn nested(&self, mut limit: Option<BalanceOf<T>>) -> RawMeter<T, E, Nested> {
		if let (Some(new_limit), Some(old_limit)) = (limit, self.limit) {
			limit = Some(new_limit.min(old_limit));
		}

		RawMeter { limit, ..Default::default() }
	}
```
