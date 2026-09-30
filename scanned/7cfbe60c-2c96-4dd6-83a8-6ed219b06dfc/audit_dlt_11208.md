# [?] fix: introduce panic-free VirtualAssertEQ via Format B immediate (#1302)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2026-03-04
Source: https://github.com/a16z/jolt/commit/3705db2cdfa3aa969f7cba857392780f53a755bd
Type: security-commit

## Details
fix: introduce panic-free VirtualAssertEQ via Format B immediate (#1302)

* feat: add VirtualSpoilProof instruction for non-panicking proof spoiling

hcf() previously emitted VirtualAssertEQ(0, 1) which panics during
tracer emulation before any proof is generated. VirtualSpoilProof
warns and continues, producing an unsatisfiable proof via the existing
R1CS Assert constraint (EqualTable(0,1) = 0 != 1).

Encoding: same opcode 0x5B / funct3 0b001 as VirtualAssertEQ,
discriminated by funct7 (0 = AssertEQ, nonzero = SpoilProof).

Guest-side hcf() now emits .insn r with funct7=1, and
unwrap_or_spoil_proof() returns zeroed memory instead of
unreachable!() since execution continues past hcf().

* chore: update Cargo.lock

* fix: address review — FormatR, hardcode 0 lookup output

- Use FormatR (matches .insn r encoding) instead of FormatB
- Hardcode to_instruction_inputs → (0, 0) and to_lookup_output → 0
- Remove materialize_entry test (intentionally inconsistent lookup)

* fix: use RangeCheckTable instead of EqualTable

RangeCheck(0, 0) = 0 is consistent with the hardcoded output,
so only the Assert constraint (output == 1) fails — single
clean failure point.

* refactor: switch VirtualAssertEQ from FormatB to FormatR

B-format encodes imm in bits[31:25], so a nonzero imm would be
misparsed as VirtualSpoilProof. Both instructions now use R-format,
cleanly discriminated by funct7 (0 = AssertEQ, nonzero = SpoilProof).

- emit_b::<VirtualAssertEQ>(rs1, rs2, 0) → emit_r(0, rs1, rs2)
- jolt-sdk .insn b → .insn r with funct7=0

* fix: replace mem::zeroed() with T::default() in UnwrapOrSpoilProof

mem::zeroed() on generic T is UB for types with validity invariants.
Add T: Default bound and use T::default() instead.

* refactor: merge VirtualSpoilProof into VirtualAssertEQ via Format B immediate

VirtualSpoilProof was a separate instruction solely to make proofs
unsatisfiable when unwrap_or_spoil_proof() fails. This is unnecessary —
VirtualAssertEQ with mismatched rs1/rs2 already produces an
unsatisfiable proof via EqualTable(x,y)=0 vs Assert flag expecting 1.

Switch VirtualAssertEQ from FormatR to FormatB and use the immediate
to distinguish assert (imm=0, panic) from spoil (imm≠0, warn). The
hcf() inline asm encodes funct7=1 which B-type decode extracts as
imm=32 (non-zero), correctly triggering spoil mode.

* refactor: replace T::default() with panic!() in unwrap_or_spoil_proof

The code after hcf() is unreachable — panic!() satisfies the type
checker without requiring T: Default.

* fix: only warn on spoil mode when rs1 != rs2

* refactor: use .insn b encoding for hcf() to match FormatB decode

* fix: return zeroed memory after hcf() instead of panicking

On RISC-V, hcf() emits a custom instruction and returns — the tracer
must continue execution. panic!() would abort the tracer. The returned
value is irrelevant since the proof is already unsatisfiable.

* fix: use panic!() after hcf() in unwrap_or_spoil_proof

* refactor: use .insn b encoding for VirtualAssertEQ in check_advice macros

## Patch
### jolt-inlines/grumpkin/src/sdk.rs
```diff
@@ -75,9 +75,9 @@ pub fn hcf() {
         let u = 0u64;
         let v = 1u64;
         core::arch::asm!(
-            ".insn b {opcode}, {funct3}, {rs1}, {rs2}, 0",
-            opcode = const 0x5B, // virtual instruction opcode
-            funct3 = const 0b001, // VirtualAssertEQ funct3
+            ".insn b {opcode}, {funct3}, {rs1}, {rs2}, . + 2",
+            opcode = const 0x5B,
+            funct3 = const 0b001,
             rs1 = in(reg) u,
             rs2 = in(reg) v,
             options(nostack)
@@ -108,7 +108,8 @@ impl<T> UnwrapOrSpoilProof<T> for Result<T, GrumpkinError> {
             Ok(v) => v,
             Err(_) => {
                 hcf();
-                unreachable!()
+                // hcf() spoils the proof; panic to satisfy the type checker
+                panic!("unwrap_or_spoil_proof failed")
             }
         }
     }
```

### jolt-inlines/secp256k1/src/sdk.rs
```diff
@@ -60,9 +60,9 @@ pub fn hcf() {
         let u = 0u64;
         let v = 1u64;
         core::arch::asm!(
-            ".insn b {opcode}, {funct3}, {rs1}, {rs2}, 0",
-            opcode = const 0x5B, // virtual instruction opcode
-            funct3 = const 0b001, // VirtualAssertEQ funct3
+            ".insn b {opcode}, {funct3}, {rs1}, {rs2}, . + 2",
+            opcode = const 0x5B,
+            funct3 = const 0b001,
             rs1 = in(reg) u,
             rs2 = in(reg) v,
             options(nostack)
@@ -135,7 +135,8 @@ impl<T> UnwrapOrSpoilProof<T> for Result<T, Secp256k1Error> {
             Ok(v) => v,
             Err(_) => {
                 hcf();
-                unreachable!()
+                // hcf() spoils the proof; panic to satisfy the type checker
+                panic!("unwrap_or_spoil_proof failed")
             }
         }
     }
```

### jolt-sdk/src/lib.rs
```diff
@@ -121,10 +121,8 @@ macro_rules! check_advice {
             let cond_value = if $cond { 1u64 } else { 0u64 };
             let expected_value = 1u64;
             unsafe {
-                // VirtualAssertEQ: assert rs1 == rs2
-                // Use B-format encoding with CUSTOM_OPCODE and FUNCT3_VIRTUAL_ASSERT_EQ
                 core::arch::asm!(
-                    ".insn b {opcode}, {funct3}, {rs1}, {rs2}, 0",
+                    ".insn b {opcode}, {funct3}, {rs1}, {rs2}, .",
                     opcode = const $crate::CUSTOM_OPCODE,
                     funct3 = const $crate::FUNCT3_VIRTUAL_ASSERT_EQ,
                     rs1 = in(reg) cond_value,
@@ -158,7 +156,7 @@ macro_rules! check_advice_eq {
             let right = $right;
             unsafe {
                 core::arch::asm!(
-                    ".insn b {opcode}, {funct3}, {rs1}, {rs2}, 0",
+                    ".insn b {opcode}, {funct3}, {rs1}, {rs2}, .",
                     opcode = const $crate::CUSTOM_OPCODE,
                     funct3 = const $crate::FUNCT3_VIRTUAL_ASSERT_EQ,
                     rs1 = in(reg) left,
```

### tracer/src/instruction/virtual_assert_eq.rs
```diff
@@ -14,10 +14,20 @@ declare_riscv_instr!(
 
 impl VirtualAssertEQ {
     fn exec(&self, cpu: &mut Cpu, _: &mut <VirtualAssertEQ as RISCVInstruction>::RAMAccess) {
-        assert_eq!(
-            cpu.x[self.operands.rs1 as usize],
-            cpu.x[self.operands.rs2 as usize]
-        );
+        if self.operands.imm == 0 {
+            assert_eq!(
+                cpu.x[self.operands.rs1 as usize],
+                cpu.x[self.operands.rs2 as usize]
+            );
+        } else {
+            let rs1 = cpu.x[self.operands.rs1 as usize];
+            let rs2 = cpu.x[self.operands.rs2 as usize];
+            if rs1 != rs2 {
+                tracing::warn!(
+                    "VirtualAssertEQ (spoil): rs1={rs1} != rs2={rs2}, proof will be unsatisfiable",
+                );
+            }
+        }
     }
 }
 
```
