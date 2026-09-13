# [H] Unsoundness in variable comparison / non-unique binary decomposition

## Summary
Severity: High
Chain: ZK
Component: Consensys/gnark
CVE: CVE-2023-44378
Published: 2023-10-03
Source: https://github.com/Consensys/gnark/security/advisories/GHSA-498w-5j49-vqjg
Type: github-advisory

## Details
### Impact

For some in-circuit values, it is possible to construct two valid decomposition to bits. In addition to the canonical decomposition of `a`, for small values there exists a second decomposition for `a+r` (where `r` is the modulus the values are being reduced by). The second decomposition was possible due to overflowing the field where the values are defined.

Internally, the comparison methods `frontend.API.Cmp` and `frontend.API.IsLess` used binary decomposition and checked the bitwise differences. This allows a malicious prover to construct a valid proof for a statement `a < b` even if `a > b`.

The issue impacts all users using `API.Cmp` or `API.IsLess` methods. Additionally, it impacts the users using `bits.ToBinary` or `API.ToBinary` methods if full-width decomposition is requested (the default behaviour if no options are given).

The issues does not impact comparison methods in field emulation (package `std/math/emulated`) and dedicated comparison package (`std/math/cmp`).

### Patches

Fix has been implemented in pull request #835 and merged in commit 59a4087261a6c73f13e80d695c17b398c3d0934f to master branch. The release v0.9.0 and onwards include the fix.

The fix added additional comparison of the decomposed bit-vector to the modulus of the in-circuit values.  

### Workarounds

Upgrading to version v0.9.0 should fix the issue without needing to change the calls to value comparison methods.

Alternatively, users can use the `std/math/cmp` gadget, which additionally allows to bound the number of bits being compared, making the comparisons more efficient if the bound on the absolute difference of the values is known.

### References

* https://github.com/Consensys/gnark/pull/835
* https://github.com/zkopru-network/zkopru/issues/116
* https://github.com/iden3/circomlib/pull/48

### Acknowledgement

The vulnerability was reported by [Marcin Kostrzewa](https://github.com/kustosz) @ [Reilabs](https://reilabs.io/).
