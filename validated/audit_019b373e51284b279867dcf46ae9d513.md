Audit Report

## Title
Integer overflow in `Memory::resize` bounds check can be bypassed on 32-bit (wasm32) targets, leading to an out-of-bounds panic in `Memory::set`/`slice_mut` - (File: substrate/frame/revive/src/vm/evm/memory.rs)

## Summary
`Memory::resize` computes `target_len = revm::interpreter::num_words(offset.saturating_add(len)) * 32` and compares it to `EVM_MEMORY_BYTES` (1 MiB) before deciding whether to grow the backing `Vec<u8>` [1](#0-0) . On a 32-bit `usize` target, this multiplication itself can wrap (`num_words(u32::MAX) * 32 == 2^32 ≡ 0 mod 2^32`), letting a spuriously small `target_len` pass the bounds check while the real requested offset remains far larger than any allocated buffer, and callers like `mstore`/`mload`/`mcopy` then index the un-grown `Vec<u8>` directly, causing a panic instead of a `Halt`.

## Finding Description
`as_usize_or_halt_with` only rejects a `U256` operand when its low limb exceeds `usize::MAX` [2](#0-1) , so on a 32-bit `usize` target an attacker-controlled EVM stack value (pushed via ordinary bytecode before `MSTORE`/`MSTORE8`/`MLOAD`/`MCOPY`) can reach up to `u32::MAX`, fully attacker-controlled and reachable through normal contract call/deploy extrinsics.

In `Memory::resize`, `offset.saturating_add(len)` correctly clamps the sum without panicking, but the subsequent `num_words(...) * 32` is not similarly protected [3](#0-2) . For `offset.saturating_add(len) = u32::MAX`, `num_words` returns `134217728`, and `134217728 * 32 = 2^32`, which wraps to `0` in 32-bit `usize` arithmetic (if overflow checks are disabled) or panics immediately (if overflow checks are enabled) — either way the check `target_len > EVM_MEMORY_BYTES` fails to reject the request as intended, or a panic occurs earlier than the documented `Halt` path.

Callers such as `mstore` and `mstore8` call `interpreter.memory.resize(offset, 32)?` and then unconditionally call `interpreter.memory.set(offset, ...)` using the original, unclamped `offset` [4](#0-3) . `Memory::set` and `Memory::slice_mut` perform raw, unchecked `self.data[offset..offset+len]` indexing, explicitly documented as panicking on out-of-bounds access [5](#0-4) [6](#0-5) . Since `self.data` was never resized to cover the huge offset when the overflow bypasses the check, this indexing panics rather than returning a graceful `Halt::Err(OutOfGas)`.

No other guard covers this gap: `as_usize_or_halt` only bounds individual `U256` values to `usize::MAX`, `saturating_add` protects only the addition step, and the `EVM_MEMORY_BYTES` comparison itself is defeated because it runs on an already-wrapped value.

## Impact Explanation
Where this is reachable, an unprivileged user can craft EVM bytecode with offsets near `usize::MAX` before a memory-touching opcode, causing an unguarded Rust panic inside contract execution instead of a controlled `Halt`. A panic during runtime execution is generally caught at higher levels (e.g., WASM trap boundaries / executive), but bypassing an intended graceful-error path in favor of an uncontrolled panic is a genuine robustness defect in the interpreter's bounds-checking logic, matching a liveness/availability class of impact rather than fund loss.

## Likelihood Explanation
The precondition (a 32-bit `usize`) only holds if this interpreter code executes in a genuinely 32-bit address-space context. This detail could not be conclusively confirmed from the available code (e.g., whether the runtime's `overflow-checks` profile setting is enabled for wasm builds, which would change whether the failure manifests as an immediate panic at the multiplication or a later out-of-bounds panic, though both paths still represent unhandled panics). The arithmetic and lack of an intermediate overflow-safe check are confirmed directly in the source and are not dependent on any exotic assumption beyond ordinary EVM operand crafting, which is realistic and requires no special privilege.

## Recommendation
Compute the memory-size bound using overflow-safe, width-independent arithmetic (e.g., perform `num_words(...) * 32` and the `EVM_MEMORY_BYTES` comparison in `u64`/`u128`, or use `checked_mul`/`saturating_mul` clamped against `EVM_MEMORY_BYTES` before ever truncating back to `usize`), so any `offset`/`len` combination whose true required size exceeds `EVM_MEMORY_BYTES` is rejected via `Halt::Err(OutOfGas)` regardless of platform `usize` width, and `Memory::set`/`slice_mut` are never reachable with an offset beyond the actually-allocated buffer.

## Proof of Concept
Add a unit test to `substrate/frame/revive/src/vm/evm/memory.rs` targeting `Memory::<Test>::resize`:
```rust
#[test]
fn resize_does_not_permit_oob_via_overflow() {
    let mut memory = Memory::<Test>::new();
    let offset = u32::MAX as usize - 31;
    let len = 32usize;
    let cf = memory.resize(offset, len);
    assert!(cf.is_break(), "resize must reject oversized offset+len, got {:?}", cf);
}
```
This test needs to run under a 32-bit `usize` target (e.g., cross-compiled to `wasm32-unknown-unknown` or a `i686` host) to reproduce the wraparound in `num_words(...) * 32`; on a 64-bit host `usize` the same inputs will correctly hit the `EVM_MEMORY_BYTES` check without wrapping, so the bug is platform-width dependent as described in the claim.

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

**File:** substrate/frame/revive/src/vm/evm/util.rs (L21-28)
```rust
pub fn as_usize_or_halt_with(value: U256, halt: impl Fn() -> Halt) -> ControlFlow<Halt, usize> {
	let limbs = value.0;
	if (limbs[0] > usize::MAX as u64) | (limbs[1] != 0) | (limbs[2] != 0) | (limbs[3] != 0) {
		ControlFlow::Break(halt())
	} else {
		ControlFlow::Continue(limbs[0] as usize)
	}
}
```

**File:** substrate/frame/revive/src/vm/evm/instructions/memory.rs (L43-61)
```rust
pub fn mstore<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
	let [offset, value] = interpreter.stack.popn()?;
	let offset = as_usize_or_halt::<E::T>(offset)?;
	interpreter.memory.resize(offset, 32)?;
	interpreter.memory.set(offset, &value.to_big_endian());
	ControlFlow::Continue(())
}

/// Implements the MSTORE8 instruction.
///
/// Stores a single byte to memory.
pub fn mstore8<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
	let [offset, value] = interpreter.stack.popn()?;
	let offset = as_usize_or_halt::<E::T>(offset)?;
	interpreter.memory.resize(offset, 1)?;
	interpreter.memory.set(offset, &[value.byte(0)]);
	ControlFlow::Continue(())
```
