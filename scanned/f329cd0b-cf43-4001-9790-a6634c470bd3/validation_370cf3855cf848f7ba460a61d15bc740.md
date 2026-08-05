### Title
Missing EVM memory-expansion gas charge allows near-free 1MB memory allocation per call in `Memory::<T>::resize` - (File: substrate/frame/revive/src/vm/evm/memory.rs)

### Summary
`Memory::<T>::resize` enforces only a hard upper bound (`EVM_MEMORY_BYTES` = 1MB) before calling `self.data.resize(target_len, 0)`, but the EVM opcode handlers that call it (`MLOAD`, `MSTORE`, `MSTORE8`, `MCOPY`, and the generic `resize_memory` used by `CALL`/`RETURN`/etc.) only charge fixed, size-independent opcode costs (`VERYLOW`=3, `BASE`=2, or `copy_cost_verylow(len)` which is proportional to `len`, not to the resulting memory size). There is no quadratic/linear memory-expansion gas surcharge tied to the new memory size the way standard EVM implementations charge it, so a single cheap opcode (e.g. `MSTORE` at offset ≈ `EVM_MEMORY_BYTES - 32`) can force a ~1MB allocation and zero-fill for a gas cost of only 3.

### Finding Description
`Memory::<T>::resize` at [1](#0-0)  computes `target_len = num_words(offset + len) * 32`, rejects it only if it exceeds `EVM_MEMORY_BYTES` (1MB, defined at [2](#0-1) ), and otherwise unconditionally performs `self.data.resize(target_len, 0)` — an allocation/zero-fill whose cost scales with `target_len`, not with any gas charged beforehand.

The call sites that trigger this resize charge only fixed, size-independent gas:
- `mload`/`mstore` charge `EVMGas(VERYLOW)` (3 gas) before calling `resize(offset, 32)` [3](#0-2) .
- `mstore8` charges `EVMGas(VERYLOW)` before `resize(offset, 1)` [4](#0-3) .
- `mcopy` charges `copy_cost_verylow(len)`, which is a function of `len` (bytes copied) only, not of `max(dst, src) + len` (the actual memory footprint after expansion) [5](#0-4) .
- Generic `resize_memory` used for `CALL`-family input/output buffers similarly resizes memory with no expansion surcharge before or after [6](#0-5) .

A search of the EVM instruction/interpreter code turned up no `memory_gas_cost`, `MemoryExpansion`, or equivalent quadratic-cost accounting anywhere in the `substrate/frame/revive/src/vm/evm` tree — the standard Ethereum memory-expansion gas formula (`memory_size_word^2/512 + 3*memory_size_word`, charged incrementally as memory grows) is not implemented. This means an attacker submitting a normal signed EVM-style `bare_call` transaction can execute a single `MSTORE`/`MLOAD` with `offset` near `EVM_MEMORY_BYTES - 32` and pay only 3 gas while forcing the runtime to allocate and zero-fill ~1MB of `Vec<u8>` inside `Memory::<T>::resize`. Because `Memory::new()` starts each call with only 4KB pre-allocated [7](#0-6) , each fresh call/transaction pays this near-1MB allocation cost from scratch, and this can be repeated across many transactions within the same block by an unprivileged caller.

### Impact Explanation
Gas charged is not proportional to actual CPU/memory work performed, violating the intended metering invariant. An attacker can craft transactions that are extremely cheap in declared EVM gas (a handful of gas units) yet force the block builder to perform up to ~1MB of allocation and zeroing work per call. Repeating this across many transactions packed into a block can inflate actual block-production wall-clock time and memory churn disproportionately to the gas/weight collected, which can degrade block production performance — the scoped impact of the question (block-production slowdown from near-limit allocations that are not gas-metered proportionally).

### Likelihood Explanation
This requires no special privileges: any account can submit a normal signed `bare_call`/EVM transaction that includes `MSTORE`/`MLOAD`/`MCOPY` with a large offset. The 1MB cap (`EVM_MEMORY_BYTES`) bounds the per-call damage, but the cost to trigger it is only a few gas units and it is trivially and repeatably reachable by any contract-calling transaction, making this a highly practical griefing vector on block-builder resources (though bounded to 1MB per call by the hard limit).

### Recommendation
Implement the standard EVM memory-expansion gas charge inside (or immediately before) `Memory::<T>::resize`: track the previous memory-size-in-words and charge the incremental cost `cost(new_words) - cost(old_words)` using the standard quadratic formula (or an equivalent weight-based charge) before performing `self.data.resize(...)`, returning `OutOfGas`/halting if the caller's remaining gas cannot cover it. Ensure `mcopy`'s gas charge also accounts for the resulting memory footprint (`max(dst, src) + len`), not just the copied length.

### Proof of Concept
Rust unit/integration test plan (in `substrate/frame/revive/src/vm/evm` test area or a `bare_call` integration test):
1. Deploy a minimal EVM bytecode contract that executes a single `PUSH... MSTORE` with `offset = EVM_MEMORY_BYTES - 32` (i.e., just under the 1MB cap).
2. Call it via `Pallet::<T>::bare_call` as a normal signed account, recording the gas charged (should be ~`VERYLOW` = 3) and the wall-clock time / `Weight` consumed by the call.
3. Repeat step 2 in a loop simulating many transactions within one block (e.g., 100 calls).
4. Assert: `gas_charged` stays constant/minimal per call while `Memory` allocation reaches `EVM_MEMORY_BYTES` each time; assert that `weight_consumed / gas_charged` ratio grows far beyond the ratio observed for calls that only touch small memory offsets (e.g., `offset = 32`), showing the metering is not proportional to actual work.
5. Optionally add a fuzz test that varies `offset` near the `EVM_MEMORY_BYTES` boundary and asserts that the incremental gas charged scales with `num_words(offset+len)` — the test should fail today since no such scaling charge exists in `resize`.

### Citations

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L31-33)
```rust
	pub fn new() -> Self {
		Self { data: Vec::with_capacity(4 * 1024), _phantom: core::marker::PhantomData }
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

**File:** substrate/frame/revive/src/limits.rs (L90-91)
```rust
/// upperbound of memory that can be used by the EVM interpreter.
pub const EVM_MEMORY_BYTES: u32 = 1024 * 1024;
```

**File:** substrate/frame/revive/src/vm/evm/instructions/memory.rs (L31-50)
```rust
pub fn mload<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
	let ([], top) = interpreter.stack.popn_top()?;
	let offset = as_usize_or_halt::<E::T>(*top)?;
	interpreter.memory.resize(offset, 32)?;
	*top = U256::from_big_endian(interpreter.memory.slice_len(offset, 32));
	ControlFlow::Continue(())
}

/// Implements the MSTORE instruction.
///
/// Stores a 32-byte word to memory.
pub fn mstore<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
	let [offset, value] = interpreter.stack.popn()?;
	let offset = as_usize_or_halt::<E::T>(offset)?;
	interpreter.memory.resize(offset, 32)?;
	interpreter.memory.set(offset, &value.to_big_endian());
	ControlFlow::Continue(())
}
```

**File:** substrate/frame/revive/src/vm/evm/instructions/memory.rs (L55-62)
```rust
pub fn mstore8<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
	let [offset, value] = interpreter.stack.popn()?;
	let offset = as_usize_or_halt::<E::T>(offset)?;
	interpreter.memory.resize(offset, 1)?;
	interpreter.memory.set(offset, &[value.byte(0)]);
	ControlFlow::Continue(())
}
```

**File:** substrate/frame/revive/src/vm/evm/instructions/memory.rs (L75-95)
```rust
pub fn mcopy<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	let [dst, src, len] = interpreter.stack.popn()?;

	// Into usize or fail
	let len = as_usize_or_halt::<E::T>(len)?;
	// Deduce gas
	let Some(gas_cost) = copy_cost_verylow(len) else {
		return ControlFlow::Break(Error::<E::T>::OutOfGas.into());
	};
	interpreter.ext.charge_or_halt(EVMGas(gas_cost))?;
	if len == 0 {
		return ControlFlow::Continue(());
	}

	let dst = as_usize_or_halt::<E::T>(dst)?;
	let src = as_usize_or_halt::<E::T>(src)?;
	// Resize memory
	interpreter.memory.resize(max(dst, src), len)?;
	// Copy memory in place
	interpreter.memory.copy(dst, src, len);
	ControlFlow::Continue(())
```

**File:** substrate/frame/revive/src/vm/evm/instructions/contract/call_helpers.rs (L42-56)
```rust
pub fn resize_memory<'a, E: Ext>(
	interpreter: &mut Interpreter<'a, E>,
	offset: U256,
	len: U256,
) -> ControlFlow<Halt, Range<usize>> {
	let len = as_usize_or_halt::<E::T>(len)?;
	if len != 0 {
		let offset = as_usize_or_halt::<E::T>(offset)?;
		interpreter.memory.resize(offset, len)?;
		ControlFlow::Continue(offset..offset + len)
	} else {
		// unrealistic value so we are sure it is not used
		ControlFlow::Continue(usize::MAX..usize::MAX)
	}
}
```
