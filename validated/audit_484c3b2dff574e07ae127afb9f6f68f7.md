### Title
Fixed `EVMGas(VERYLOW)` charge for `MSTORE`/`MLOAD`/`MSTORE8` does not scale with memory-expansion cost, allowing near-max memory zero-fill for a flat, tiny fee - (File: substrate/frame/revive/src/vm/evm/instructions/memory.rs)

### Summary
`mload`, `mstore`, and `mstore8` each charge a single fixed `EVMGas(VERYLOW)` token regardless of how far the memory offset requires `Memory::resize` to grow the buffer [1](#0-0) . `Memory::resize` performs an actual `Vec::resize` (zero-fill) of up to `EVM_MEMORY_BYTES` (1 MiB) in a single call and only enforces a hard cap — it charges no gas proportional to the bytes touched [2](#0-1) . Unlike upstream EVM, which charges a quadratic `memory_expansion_cost` precisely to prevent single-opcode large allocations, this implementation has no such cost for `MLOAD`/`MSTORE`/`MSTORE8`.

### Finding Description
In `mstore`, `mload`, `mstore8` (substrate/frame/revive/src/vm/evm/instructions/memory.rs:31-62), the only gas/weight charge is the constant `EVMGas(VERYLOW)`, which is converted to `Weight` via `T::WeightInfo::evm_opcode(1) - evm_opcode(0)` — a fixed per-opcode weight independent of the `offset` operand [3](#0-2) .

The actual work is done in `Memory::resize`, which computes `target_len` from the attacker-controlled `offset` and unconditionally performs `self.data.resize(target_len, 0)` when growing, bounded only by the hard cap `EVM_MEMORY_BYTES` (1 MiB) [2](#0-1) [4](#0-3) . Since a fresh call frame starts with `Memory::new()` (an essentially empty buffer) [5](#0-4) , a single `MSTORE` with `offset = EVM_MEMORY_BYTES - 32` triggers one `resize` call that zero-fills close to 1 MiB of memory — for the exact same fixed `VERYLOW` charge as an `MSTORE` at offset 0. There is no length- or offset-dependent cost added anywhere in this path (contrast with `calldatacopy`/`codecopy`/`returndatacopy`, which do charge `RuntimeCosts::CopyToContract(len)` scaled by copy length [6](#0-5) ).

This is confirmed by the existing test `memory_limit_works`, which shows that a single call expanding memory up to `EVM_MEMORY_BYTES - 1` succeeds under the pallet's own gas/weight accounting rather than failing due to any resize-proportional cost [7](#0-6) .

Because `charge_or_halt` gates on the `WeightMeter`'s `effective_weight_limit`/frame gas limit and not on the physical cost of the memory buffer resize, an attacker's per-instruction weight bill for a maximal single-shot memory expansion is identical to a trivial no-op memory write.

### Impact Explanation
An attacker-controlled contract can be crafted so that each external call performs one (or a few) `MSTORE` operations at large offsets close to the 1 MiB `EVM_MEMORY_BYTES` cap, forcing the runtime to allocate/zero close to 1 MiB of heap memory per call while billing only the flat `VERYLOW` weight/fee. By issuing many such calls within a block (limited only by the aggregate block weight budget, which under-represents the true CPU/memory cost of the resize), an attacker can drive substantially more real CPU/memory work per unit of billed weight than a legitimate contract that grows memory incrementally. This can degrade block-production throughput/timing for other transactions in the same block while the attacker under-pays via `pallet_transaction_payment`, matching the "fee/weight logic must not be bypassable by normal users" invariant.

### Likelihood Explanation
The precondition is simply deploying and calling an EVM-compatible contract on `pallet_revive` (permissionless, standard `eth_transact`/contract-call path) that executes `MSTORE`/`MLOAD` with a large offset operand. No privileged origin, proxy, or XCM path is required — a plain signed contract call suffices, and the behavior is deterministic/repeatable across every call. The magnitude of the exploitable gap (fixed benchmarked `evm_opcode` weight vs. real cost of a ~1 MiB `Vec::resize`) could not be fully quantified here because the benchmarking machinery for `evm_opcode` (in `substrate/frame/revive/src/weights.rs`, auto-generated) was not fully inspected in this session — it is possible (but not confirmed) that the benchmark for `evm_opcode` was already calibrated using a worst-case memory-heavy opcode, which would reduce or eliminate the practical gap. This should be validated with an actual CPU-time benchmark before treating the severity as certain.

### Recommendation
Introduce an explicit memory-expansion charge (analogous to EVM's `memory_expansion_cost`, or at minimum a charge proportional to `target_len - current_len`) inside `Memory::resize`, charged via the frame's meter before the zero-fill occurs, so that `MLOAD`/`MSTORE`/`MSTORE8`/`MCOPY` bill weight proportional to the actual bytes touched rather than a single flat `VERYLOW` cost.

### Proof of Concept
Rust benchmark/integration test plan:
1. In `substrate/frame/revive/src/tests/sol/memory.rs`, add a test that measures wall-clock time (or instruction/fuel count) of a single `MSTORE`-style call with `offset = EVM_MEMORY_BYTES - 32` versus `offset = 0`, both via `bare_call`.
2. Assert the weight/gas actually deducted from the frame meter (obtainable via the `GasMeter`/`WeightMeter` trace, e.g. through `builder::bare_call` result's consumed weight) is identical for both offsets (demonstrating the flat charge).
3. Separately, instrument or benchmark `Memory::resize` directly (as a Rust unit test in `substrate/frame/revive/src/vm/evm/memory.rs`) to measure real CPU time for `resize(EVM_MEMORY_BYTES - 32, 32)` starting from an empty `Memory`, and assert that this time is orders of magnitude larger than `resize(0, 32)`, while the corresponding `T::WeightInfo::evm_opcode` delta remains constant — proving the accounting mismatch.
4. Fuzz test: for a set of offsets `[0, EVM_MEMORY_BYTES/4, EVM_MEMORY_BYTES/2, EVM_MEMORY_BYTES - 32]`, assert that weight charged scales at least linearly with `offset`; expect the assertion to fail against current code (constant charge), demonstrating the bug.

### Citations

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

**File:** substrate/frame/revive/src/vm/evm/memory.rs (L29-33)
```rust
impl<T: Config> Memory<T> {
	/// Create a new empty memory
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

**File:** substrate/frame/revive/src/vm/evm.rs (L57-62)
```rust
impl<T: Config> Token<T> for EVMGas {
	fn weight(&self) -> Weight {
		let base_cost = T::WeightInfo::evm_opcode(1).saturating_sub(T::WeightInfo::evm_opcode(0));
		base_cost.saturating_mul(self.0)
	}
}
```

**File:** substrate/frame/revive/src/limits.rs (L90-91)
```rust
/// upperbound of memory that can be used by the EVM interpreter.
pub const EVM_MEMORY_BYTES: u32 = 1024 * 1024;
```

**File:** substrate/frame/revive/src/vm/evm/instructions/system.rs (L206-222)
```rust
/// Common logic for copying data from a source buffer to the EVM's memory.
///
/// Handles memory expansion and gas calculation for data copy operations.
pub fn memory_resize<'a, E: Ext>(
	interpreter: &mut Interpreter<'a, E>,
	memory_offset: U256,
	len: usize,
) -> ControlFlow<Halt, Option<usize>> {
	if len == 0 {
		return ControlFlow::Continue(None);
	}

	interpreter.ext.charge_or_halt(RuntimeCosts::CopyToContract(len as u32))?;
	let memory_offset = as_usize_or_halt::<E::T>(memory_offset)?;
	interpreter.memory.resize(memory_offset, len)?;
	ControlFlow::Continue(Some(memory_offset))
}
```

**File:** substrate/frame/revive/src/tests/sol/memory.rs (L40-47)
```rust
		let test_cases = [
			(
				"Writing 1 byte from 0 to the limit - 1 should work.",
				Memory::expandMemoryCall {
					memorySize: (crate::limits::EVM_MEMORY_BYTES - 1) as u64,
				},
				Ok(ExecReturnValue { data: vec![0u8; 32], flags: ReturnFlags::empty() }),
			),
```
