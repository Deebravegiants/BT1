[1](#0-0)

### Citations

**File:** aptos-move/aptos-gas-schedule/src/gas_schedule/instr.rs (L15-26)
```rust
crate::gas_schedule::macros::define_gas_parameters!(
    InstructionGasParameters,
    "instr",
    VMGasParameters => .instr,
    [
        // nop
        [nop: InternalGas, "nop", 360],
        // control flow
        [ret: InternalGas, "ret", 2200],
        [abort: InternalGas, "abort", 2200],
        [abort_msg_base: InternalGas, { RELEASE_V1_40.. => "abort_msg.base" }, 4400],
        [abort_msg_per_byte: InternalGasPerByte, { RELEASE_V1_40.. => "abort_msg.per_byte" }, 450],
```
