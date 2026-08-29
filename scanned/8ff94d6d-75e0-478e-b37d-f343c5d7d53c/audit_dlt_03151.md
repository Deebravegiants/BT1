# [H] Potentially sensitive issue - disclosed privately

## Summary
Severity: High
Chain: Smart contract
Component: 2023-10-zksync
Published: 2023-10-23
Source: https://github.com/code-423n4/2023-10-zksync-findings/issues/697
Type: code-finding

## Details
The `main_vm` circuit uses a `MulDivRelation` to constrain the result of a `shr` instruction by converting a right shift into a division by a shift constant.

https://github.com/code-423n4/2023-10-zksync/blob/main/code/era-zkevm_circuits/src/main_vm/opcodes/shifts.rs#L76

```rust
let full_shift_limbs = get_shift_constant(cs, full_shift);
...
let (rshift_q, _rshift_r) = allocate_div_result_unchecked(cs, &reg, &full_shift_limbs);
...
// actual enforcement:
// for left_shift: a = reg, b = full_shuft, remainder = 0, high = lshift_high, low = lshift_low
// for right_shift : a = rshift_q, b = full_shift, remainder = rshift_r, high = 0, low = reg
let uint256_zero = UInt256::zero(cs);

let rem_to_enforce =
    UInt32::parallel_select(cs, apply_left_shift, &uint256_zero.inner, &_rshift_r);
let a_to_enforce = UInt32::parallel_select(cs, apply_left_shift, reg, &rshift_q);
let b_to_enforce = full_shift_limbs;
let mul_low_to_enforce = UInt32::parallel_select(cs, apply_left_shift, &lshift_low, reg);
let mul_high_to_enforce =
    UInt32::parallel_select(cs, apply_left_shift, &lshift_high, &uint256_zero.inner);

let mul_relation = MulDivRelation {
    a: a_to_enforce,
    b: b_to_enforce,
    rem: rem_to_enforce,
    mul_low: mul_low_to_enforce,
    mul_high: mul_high_to_enforce,
};
```

However, the circuit fails to constrain the remainder to be less than the divisor. This allows a malicious prover to set the result to any value less than or equal to the correct result (and possibly any value, but this has not be verified).

## Impact
A malicious validator could generate and submit a proof with incorrect behavior of the `shr` instruction. This would allow the validator to manipulate the behavior of smart contracts that use a `shr` instruction. For example, the validator could manipulate the calculated price during the execution of an on-chain DEX and steal all of the assets in the DEX. The elliptic curve precompiles also make extensive use of shift instructions. Since every smart contract that uses a `shr` instruction is affected, it is impossible to enumerate all potential impacts.

This vulnerability also affects the deployed circuits that utilize bellman instead of boojum.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-zksync-findings/issues/697_
