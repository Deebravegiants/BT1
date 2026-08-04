### Title
Integer overflow in `Memory::resize` bounds check can be bypassed on 32-bit (wasm32) targets, leading to an out-of-bounds panic in `Memory::set`/`slice_mut` - (File: substrate/frame/revive/src/vm/evm/memory.rs)

### Summary
`Memory::resize` computes `target_len = revm::interpreter::num_words(offset.saturating_add(len)) * 32` and compares it against `EVM_MEMORY_BYTES` (1 MiB) to decide whether to grow the backing `Vec<u8>`. On a 32-bit `usize` target (the WASM runtime used for on-chain execution is `wasm32`, where `usize` is 32 bits), attacker-supplied EVM opcode operands (e.g. `MSTORE`, `CALL`, `LOG`, `EXTCODECOPY` offsets/lengths) can drive the internal word-count-times-32 multiplication to wrap around `2^32`, producing a spuriously small `target_len` that passes the `EVM_MEMORY_BYTES` check without actually growing memory. The subsequent `Memory::set`/`Memory::slice_mut` call then indexes the underlying `Vec<u8>` with the original (huge) `offset`, causing an unguarded slice-index panic instead of a graceful `Halt`.

### Finding Description
`as_usize_or_halt_with` (`substrate/frame/revive/src/vm/evm/util.rs:21-28`) only rejects a `U256` if its low limb exceeds `usize::MAX`, so on `wasm32` an attacker can set `offset` or `len` to values up to `u32::MAX` (≈4.29B) via ordinary EVM stack operands — fully attacker-controlled through bytecode of a deployed/called contract.

In `Memory::resize` (`substrate/frame/revive/src/vm/evm/memory.rs:66-79`):
```rust
let target_len = revm::interpreter::num_words(offset.saturating_add(len)) * 32;
if target_len > crate::limits::EVM_MEMORY_BYTES as usize {
    return ControlFlow::Break(Error::<T>::OutOfGas.into());
}
``` [1](#0-0) 

`offset.saturating_add(len)` correctly caps the sum at `usize::MAX` without panicking. However, when this saturated value is close to `usize::MAX` (i.e. `u32::MAX` on wasm32), `num_words(x) * 32` can itself overflow the 32-bit `usize`: e.g. `num_words(u32::MAX) == 134217728`, and `134217728 * 32 == 2^32`, which wraps to `0` in a non-overflow-checked (release/production wasm) build. This makes `target_len` pass the `EVM_MEMORY_BYTES` check (`0 <= 1_048_576`) even though the real `offset+len` is billions of bytes, and the underlying `Vec<u8>` is never grown to cover it.

Callers such as `mstore`/`mstore8` (`substrate/frame/revive/src/vm/evm/instructions/memory.rs:43-61`) call `interpreter.memory.resize(offset, 32)?` and then unconditionally call `interpreter.memory.set(offset, &value.to_big_endian())` using the *original, un-clamped* `offset`. `Memory::set`/`Memory::slice_mut` (`substrate/frame/revive/src/vm/evm/memory.rs:52-54, 86-90`) perform raw `self.data[offset..offset+len]` indexing with no bounds check ("Panics on out of bounds" is explicitly documented). Since `self.data` was never actually resized to cover this offset, this indexing operation panics. [2](#0-1) [3](#0-2) 

No existing check protects against this: `as_usize_or_halt` only bounds individual `U256` values to `usize::MAX`, `saturating_add` protects only the addition (not the subsequent `num_words(...) * 32`), and `EVM_MEMORY_BYTES` comparison is defeated by the wraparound before it ever runs.

### Impact Explanation
An unprivileged user can deploy or call an EVM contract (via pallet-revive's normal, permissionless `call`/`instantiate` extrinsic paths) containing crafted bytecode that pushes an offset near `u32::MAX` before `MSTORE`/`MSTORE8`/`CALL`/`LOG`/`EXTCODECOPY`. When the runtime executes this on a 32-bit (`wasm32`) target, the overflow causes an unguarded Rust panic (slice index out of bounds) instead of a controlled `ControlFlow::Break(Halt::Err(...))`. A panic inside runtime execution (a WASM trap) aborts the extrinsic/block execution path rather than failing gracefully, which can make a block containing the transaction unprocessable — a liveness/DoS impact on the specific execution rather than an asset-theft impact.

### Likelihood Explanation
Feasible for any unprivileged caller who can deploy/execute EVM contract bytecode in pallet-revive; it requires no special privileges, only crafting stack values near `u32::MAX` before a memory-touching opcode, and only manifests where `usize` is 32 bits (the standard `wasm32` on-chain runtime execution environment), making it realistically reachable in production parachain/relay execution.

### Recommendation
Compute `target_len` using overflow-safe arithmetic end-to-end (e.g. `checked_add`/`saturating_mul` clamped to `EVM_MEMORY_BYTES`, or perform the bounds comparison in a wider integer type such as `u64`/`u128` before truncating), so that any `offset`/`len` combination that would exceed `EVM_MEMORY_BYTES` is rejected with `Halt::Err(OutOfGas)` regardless of `usize` width, and never silently wraps to a small `target_len`.

### Proof of Concept
Add a fuzz/unit test in `substrate/frame/revive/src/vm/evm/memory.rs` targeting `Memory::<Test>::resize` (compiled for a 32-bit target, e.g. `wasm32-unknown-unknown` test target or by simulating with `u32`-sized arithmetic):
```rust
#[test]
fn resize_does_not_permit_oob_via_overflow() {
    let mut memory = Memory::<Test>::new();
    // Values chosen so num_words(offset+len)*32 wraps to a small usize on 32-bit targets.
    let offset = u32::MAX as usize - 31;
    let len = 32usize;
    let cf = memory.resize(offset, len);
    // Must halt gracefully, not report success with undersized backing buffer.
    assert!(cf.is_break());
    // If (incorrectly) continue, the following must not panic:
    if cf.is_continue() {
        memory.set(offset, &[0u8; 32]); // should not panic
    }
}
```
Expected assertion: `resize` must return `ControlFlow::Break(Halt::Err(OutOfGas))` for any `(offset, len)` pair whose true sum exceeds `EVM_MEMORY_BYTES`, and `Memory::set`/`slice_mut` must never be reachable with an out-of-bounds `offset` after a `Continue` result.

### Citations

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L52-54)
```rust
	pub fn slice_mut(&mut self, offset: usize, len: usize) -> &mut [u8] {
		&mut self.data[offset..offset + len]
	}
```

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L66-79)
```rust
	pub fn resize(&mut self, offset: usize, len: usize) -> ControlFlow<Halt> {
		let current_len = self.data.len();
		let target_len = revm::interpreter::num_words(offset.saturating_add(len)) * 32;
		if target_len > crate::limits::EVM_MEMORY_BYTES as usize {
			log::debug!(target: crate::LOG_TARGET, "check memory bounds failed: offset={offset} target_len={target_len} current_len={current_len}");
			return ControlFlow::Break(Error::<T>::OutOfGas.into());
		}

		if target_len > current_len {
			self.data.resize(target_len, 0);
		}

		ControlFlow::Continue(())
	}
```

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L86-90)
```rust
	pub fn set(&mut self, offset: usize, data: &[u8]) {
		if !data.is_empty() {
			self.data[offset..offset + data.len()].copy_from_slice(data);
		}
	}
```
