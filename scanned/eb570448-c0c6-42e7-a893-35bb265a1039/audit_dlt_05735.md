# [M] # Attackathon _ Fuel Network 32768 - [Blockchain_DLT - Medium] WDCM and WQCM doesnt respect the fuel-s

## Summary
Severity: Medium
Chain: Blockchain/DLT
Component: Fuel Network | Attackathon
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2032768%20-%20%5BBlockchain_DLT%20-%20Medium%5D%20WDCM%20and%20WQCM%20doesnt%20respect%20the%20fuel-specs.md
Type: immunefi-boost

## Details
Target: https://github.com/FuelLabs/fuel-vm/tree/0e46d324da460f2db8bcef51920fb9246ac2143b

## Description

## Brief/Intro

According to the fuel-specs, both [WDCM](https://github.com/FuelLabs/fuel-specs/blob/master/src/fuel-vm/instruction-set.md#wdcm-128-bit-integer-comparison) and [WQCM](https://github.com/FuelLabs/fuel-specs/blob/master/src/fuel-vm/instruction-set.md#wqcm-256-bit-integer-comparison) should clears $of and $err registers, but those two instruction don't clear these regs.

## Vulnerability Details

I will take WDCM as example: In [WDCM](https://github.com/FuelLabs/fuel-vm/blob/0e46d324da460f2db8bcef51920fb9246ac2143b/fuel-vm/src/interpreter/executors/instruction.rs#L196-L202), self.alu\_wideint\_cmp\_u256 will be called, and self.alu\_wideint\_cmp\_u256 is defined as a [macro](https://github.com/FuelLabs/fuel-vm/blob/0e46d324da460f2db8bcef51920fb9246ac2143b/fuel-vm/src/interpreter/alu/wideint.rs#L71-L95)

```rust
 73                 pub(crate) fn [<alu_wideint_cmp_ $t:lower>](
 74                     &mut self,
 75                     ra: RegisterId,
 76                     b: Word,
 77                     c: Word,
 78                     args: CompareArgs,
 79                 ) -> SimpleResult<()> {
 80                     let (SystemRegisters { pc, .. }, mut w) = split_registers(&mut self.registers);
 81                     let dest: &mut Word = &mut w[ra.try_into()?];
 82 
 83                     // LHS argument is always indirect, load it
 84                     let lhs: $t = $t::from_be_bytes(self.memory.as_ref().read_bytes(b)?);
 85 
 86                     // RHS is only indirect if the flag is set
 87                     let rhs: $t = if args.indirect_rhs {
 88                         $t::from_be_bytes(self.memory.as_ref().read_bytes(c)?)
 89                     } else {
 90                         c.into()
 91                     };
 92 
 93                     *dest = [<cmp_ $t:lower>](lhs, rhs, args.mode);
 94 
 95                     inc_pc(pc)?;
 96                     Ok(())
 97                 }
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Fuel%20Network%20%7C%20Attackathon/Attackathon%20_%20Fuel%20Network%2032768%20-%20%5BBlockchain_DLT%20-%20Medium%5D%20WDCM%20and%20WQCM%20doesnt%20respect%20the%20fuel-specs.md_
