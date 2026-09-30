# [H] Jalr imm_sign is unconstrained

## Summary
Severity: High
Reporter: cergyk
Contest weight: 0.7291
Dataset id: 4878
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Jalr opcode circuit, there is a flag to sign extend the 12 bit immediate passed to the
instruction:
```solidity
//@audit additional term because of sign extending the immediate
let imm_extend_limb = imm_sign * AB::F::from_canonical_u32((1 << 16) - 1);
let carry = (rs1_limbs_23 + imm_extend_limb + carry - to_pc_limbs[1]) * inv;
builder.when(is_valid).assert_bool(carry);
```
Unfortunately imm_sign is not constrained, thus the prover can decide to make imm_extend_limb zero or
((1 << 16) - 1) and change program flow.

## Recommendation
Consider adding a constrain asserting that imm_sign is 1 iff higher bit of imm is 1:
```solidity
+ self.range_bus
+
.range_check(imm - imm_sign * AB::F::from_canonical_u16(1 << 15), 15)
+
.eval(builder, is_valid);
```
