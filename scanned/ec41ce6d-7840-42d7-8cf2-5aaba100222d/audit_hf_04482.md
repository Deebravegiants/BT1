# [M] `ExponentiationImpl::pow`

## Summary
Severity: Medium
Contest weight: 0.2328
Dataset id: 22030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The [`ExponentiationImpl::pow()`](https://github.com/kkrt-labs/kakarot-ssj/blob/d4a7873d6f071813165ca7c7adb2f029287d14ca/crates/utils/src/math.cairo#L39) function in `math.cairo` incorrectly returns `0` when computing `0^0`, instead of the mathematically accepted value of 1. This breaks a fundamental mathematical convention that is relied upon in many mathematical contexts, including polynomial evaluation, Taylor series, and combinatorial calculations.

The issue occurs because the function first checks if the base is zero and returns zero if true, without considering the special case where the exponent is also zero. This early return means that `0^0` evaluates to `0` instead of 1:

    fn pow(self: T, mut exponent: T) -> T {
    	let zero = Zero::zero();
    	if self.is_zero() {
    		return zero;
    	}
    	...

The mathematical definition of `0^0 = 1` is not arbitrary. It is the natural definition that makes many mathematical formulas and theorems work correctly. For example, this definition is necessary for:

  * The binomial theorem to work correctly when `x=0`.
  * Power series expansions to be valid at `x=0`.
  * Combinatorial formulas involving empty sets.
  * Preserving continuity in certain mathematical limits.

This function is not currently being used to compute `0^0` in the code in scope. However, given the critical nature of the function and fundamental incorrectness of its output, the expectation of this issue causing vulnerabilities in [future code](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization#speculation-on-future-code) is fulfilled.

## Recommendation
Add a check for the `0^0` case before checking if the base is zero:

    fn pow(self: T, mut exponent: T) -> T {
        // Handle 0^0 case first
        if self.is_zero() && exponent.is_zero() {
            return One::one();
        }
        
        // Rest of the existing function...
        if self.is_zero() {
            return Zero::zero();
        }
        // ...
    }

This change preserves the mathematically correct behavior while maintaining all other functionality of the power function.

> Severity: Medium

> [PR 1579](https://github.com/kkrt-labs/kakarot/pull/1579) and [ssj PR 1022](https://github.com/kkrt-labs/kakarot-ssj/pull/1022) fixes pow in SSJ.
