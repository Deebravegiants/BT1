[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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
