### Title
Integer overflow in `Memory::resize` word-rounding calculation lets attacker-crafted RETURN/REVERT offset/len panic the runtime - ([File: substrate/frame/revive/src/vm/evm/memory.rs])

### Summary
`Memory::resize` computes `revm::interpreter::num_words(offset.saturating_add(len)) * 32` to derive the target buffer length before checking it against `EVM_MEMORY_BYTES`. When `offset` is crafted close to `usize::MAX`, `offset.saturating_add(len)` clamps to `usize::MAX`, and rounding that value up to the next 32-byte word and multiplying by 32 overflows `usize` (e.g. `num_words(usize::MAX) * 32 == 2^64` on a 64-bit target). This overflow either panics directly (if overflow checks are enabled) or wraps to a small value that incorrectly passes the `EVM_MEMORY_BYTES` bound check, after which `return_inner`'s subsequent `interpreter.memory.slice_len(offset, len)` indexes `self.data[offset..offset+len]` with the original huge `offset`, causing an out-of-bounds slice panic.

### Finding Description
`return_inner` in `substrate/frame/revive/src/vm/evm/instructions/control.rs` (lines 93-109) pops `offset`/`len` from the EVM stack, converts them to `usize` via `as_usize_or_halt`, and calls: [1](#0-0) 

`as_usize_or_halt`/`as_usize_or_halt_with` only reject a `U256` if its value doesn't fit into a single 64-bit limb (i.e. `>= 2^64`); any value up to `usize::MAX` (0xFFFF...FFFF) is accepted: [2](#0-1) 

`Memory::resize` then computes the target buffer length as: [3](#0-2) 

The `offset.saturating_add(len)` prevents overflow of the *addition*, but the result is fed into `revm::interpreter::num_words(x) * 32`. `num_words` rounds `x` up to the next multiple of 32; when `x == usize::MAX`, rounding up and multiplying by 32 produces `2^64`, which overflows `usize` on a 64-bit target. Depending on build profile:
- With overflow checks enabled, the multiplication itself panics inside `resize`.
- Without overflow checks, the multiplication wraps to a small value (e.g. near 0), which then incorrectly passes the `target_len > EVM_MEMORY_BYTES` guard, so `resize` reports success (`ControlFlow::Continue`) without actually growing `self.data` to cover the attacker's `offset`.

In the second (wrap) case, `return_inner` proceeds to call `interpreter.memory.slice_len(offset, len)`, which does `&self.data[offset..offset+len]` with the original huge `offset` against a tiny `self.data` — an out-of-bounds slice index that panics: [4](#0-3) 

The same unsafe pattern (`resize` followed by `slice_len`/`slice_mut` with the same offset/len) is reused throughout the EVM instruction set (`mload`, `keccak256`, `mcopy`, `extcodecopy`, etc.), but `RETURN`/`REVERT` are directly and trivially reachable by any attacker-supplied bytecode with a single `PUSH`, `PUSH`, `RETURN` sequence, requiring no special preconditions or gas budgeting beyond the normal contract-call gas metering.

### Impact Explanation
A successful crafted `RETURN`/`REVERT` call triggers a Rust panic (either an arithmetic-overflow panic in `resize`, or an out-of-bounds slice panic in `slice_len`) instead of returning a graceful `Halt::Err`. Panics inside runtime/STF execution abort transaction/block processing, which — depending on how the panic propagates through the executive and whether it is caught by `panic = 'unwind'`/`catch_unwind` wrappers in the node — can halt block production or at minimum crash the node executing that block, since this code runs inside pallet-revive's EVM interpreter invoked from a normal (unprivileged) contract call extrinsic.

### Likelihood Explanation
Fully attacker-controlled and requires no privilege: any account can deploy trivial EVM bytecode consisting of `PUSH32 0xFFFFFFFFFFFFFFFF` (offset near `usize::MAX`), `PUSH1 <len>`, `RETURN`, and invoke it via a normal `call`/`instantiate` extrinsic against `pallet-revive`. `as_usize_or_halt` does not reject offsets up to `usize::MAX`, so the crafted stack values pass validation and reach `Memory::resize` unmodified. This is deterministically repeatable on every call.

### Recommendation
In `Memory::resize` (substrate/frame/revive/src/vm/evm/memory.rs), bound-check `offset` and `len` (and their sum) against `EVM_MEMORY_BYTES` *before* computing `num_words(...) * 32`, e.g. reject early if `offset > EVM_MEMORY_BYTES as usize || len > EVM_MEMORY_BYTES as usize || offset.saturating_add(len) > EVM_MEMORY_BYTES as usize`, using checked/saturating arithmetic throughout so no downstream multiplication or addition can wrap. Additionally, add a final consistency assertion (`debug_assert!` is insufficient for production; use a real check) in `return_inner`/`slice_len` call sites that `offset + len <= self.data.len()` before slicing, returning `Halt::Err` instead of indexing.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/vm/evm/memory.rs` tests module:
```rust
#[test]
fn resize_with_near_max_offset_does_not_panic_or_corrupt() {
    let mut memory = Memory::<Test>::new();
    // offset chosen so offset + len saturates to usize::MAX
    let offset = usize::MAX - 10;
    let len = 100usize;
    let result = memory.resize(offset, len);
    // Expect graceful halt, not a panic and not an incorrect Continue
    assert!(result.is_break(), "resize must reject an out-of-range offset/len combo");
}
```
And an integration-level PoC via `builder::bare_call` with EVM bytecode `PUSH32 0xFFFFFFFFFFFFFFFF PUSH1 0x20 RETURN` (or `REVERT`), asserting the call result is a graceful `Err(...)` (e.g. `Error::<Test>::OutOfGas`) and that the test process does not panic — run under `cargo test -- --nocapture` with `overflow-checks = true` (as configured in the workspace `Cargo.toml`) to confirm the overflow panic is caught by the fix rather than propagating.

### Citations

**File:** substrate/frame/revive/src/vm/evm/instructions/control.rs (L102-106)
```rust
	if len != 0 {
		let offset = as_usize_or_halt::<E::T>(offset)?;
		interpreter.memory.resize(offset, len)?;
		output = interpreter.memory.slice_len(offset, len).to_vec()
	}
```

**File:** substrate/frame/revive/src/vm/evm/util.rs (L20-34)
```rust
/// Helper function to convert U256 to usize, checking for overflow
pub fn as_usize_or_halt_with(value: U256, halt: impl Fn() -> Halt) -> ControlFlow<Halt, usize> {
	let limbs = value.0;
	if (limbs[0] > usize::MAX as u64) | (limbs[1] != 0) | (limbs[2] != 0) | (limbs[3] != 0) {
		ControlFlow::Break(halt())
	} else {
		ControlFlow::Continue(limbs[0] as usize)
	}
}

/// Helper function to convert U256 to usize, checking for overflow, with default OutOfGas
/// error
pub fn as_usize_or_halt<T: Config>(value: U256) -> ControlFlow<Halt, usize> {
	as_usize_or_halt_with(value, || Error::<T>::OutOfGas.into())
}
```

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L65-79)
```rust
	/// Resize memory to accommodate the given offset and length
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

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L116-123)
```rust
	/// Returns a byte slice of the memory region at the given offset.
	///
	/// # Panics
	///
	/// Panics on out of bounds.
	pub fn slice_len(&self, offset: usize, size: usize) -> &[u8] {
		&self.data[offset..offset + size]
	}
```
