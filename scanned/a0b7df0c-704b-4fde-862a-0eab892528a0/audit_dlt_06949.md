# [M] `ExponentiationImpl::pow()` returns 0 for 0^0

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-kakarot
Published: 2024-10-25
Source: https://github.com/code-423n4/2024-09-kakarot-findings/issues/65
Type: code-finding

## Details
# Lines of code

https://github.com/kkrt-labs/kakarot-ssj/blob/d4a7873d6f071813165ca7c7adb2f029287d14ca/crates/utils/src/math.cairo#L41


# Vulnerability details

The [`ExponentiationImpl::pow()`](https://github.com/kkrt-labs/kakarot-ssj/blob/d4a7873d6f071813165ca7c7adb2f029287d14ca/crates/utils/src/math.cairo#L39) function in `math.cairo` incorrectly returns 0 when computing 0^0, instead of the mathematically accepted value of 1. This breaks a fundamental mathematical convention that is relied upon in many mathematical contexts, including polynomial evaluation, Taylor series, and combinatorial calculations.

The issue occurs because the function first checks if the base is zero and returns zero if true, without considering the special case where the exponent is also zero. This early return means that 0^0 evaluates to 0 instead of 1:

```rust
fn pow(self: T, mut exponent: T) -> T {
	let zero = Zero::zero();
	if self.is_zero() {
		return zero;
	}
	...
```

The mathematical definition of 0^0 = 1 is not arbitrary - it is the natural definition that makes many mathematical formulas and theorems work correctly. For example, this definition is necessary for:
- The binomial theorem to work correctly when x=0
- Power series expansions to be valid at x=0
- Combinatorial formulas involving empty sets
- Preserving continuity in certain mathematical limits

This function is not currently being used to compute 0^0 in the code in scope. However, given the critical nature of the function and fundamental incorrectness of its output, the expectation of this issue causing vulnerabilities in [future code](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization#speculation-on-future-code) is fulfilled.

## Impact
- Mathematical operations that rely on the standard convention of 0^0 = 1 will produce incorrect results
- Future code that reaches this case in core Kakarot contracts, protocols built on top of Kakarot's codebase or borrowing from it will experience material errors when processing edge cases

## Proof of Concept
N/A

## Recommended Mitigation Steps
Add a check for the 0^0 case before checking if the base is zero:


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-kakarot-findings/issues/65_
