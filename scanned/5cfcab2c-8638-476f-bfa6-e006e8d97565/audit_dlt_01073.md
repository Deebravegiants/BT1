# [H] soroban-fixed-point-math has Incorrect Rounding and Overflow Handling in Signed Fixed-Point Math with Negatives

## Summary
Severity: High
Chain: soroban-fixed-point-math
Component: soroban-fixed-point-math, soroban-fixed-point-math
CVE: CVE-2026-24783
CWE: Incorrect Calculation
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-x5m4-43jf-hh65
Type: github-advisory

## Details
### Impact

#### Incorrect rounding direction for signed mul and div operations

The `mulDiv(x, y, z)` function incorrectly handled cases where both the intermediate product $x * y$ and the divisor $z$ were negative. The logic assumed that if the intermediate product was negative, the final result must also be negative, neglecting the sign of $z$.

This resulted in rounding being applied in the wrong direction for cases where both $x * y$ and $z$ were negative. The functions most at risk are `fixed_div_floor` and `fixed_div_ceil`, as they often use non-constant numbers as the divisor $z$ in `mulDiv`. 

This error is present in all signed `FixedPoint` and `SorobanFixedPoint` implementations, including `i64`, `i128`, and `I256`.

#### Negative Overflow in `i64`

The `mulDiv(x, y, z)` function for `i64` used the `i128` type to handle "phantom overflows". These are overflows that occur intermediately during a calculation, like when computing the intermediate product $x * y$. When the final result of `mulDiv` was computed in `i128`, it was scaled back down to `i64` before returning. While the code verified that the result did not exceed `i64::MAX`, it did not check against `i64::MIN`.

This caused negative results smaller than `i64:MIN` to wrap around to a large positive number instead of being caught as an overflow.

This error only exists for the `FixedPoint` implementation of `i64`. 

### Patches

* v1.3.0 users should upgrade to patch v1.3.1
* v1.4.0 users should upgrade to patch v1.4.1

All versions `>=v1.4.1` contain the patch. 

### Workarounds
There are no known workarounds. Upgrade to the patched version.

### Credits

soroban-fixed-point-math would like to thank the team at [Certora](https://www.certora.com/) for discovering and reporting the issue.
