# [C] Out of bounds write in nalgebra

## Summary
Severity: Critical
Advisory: GHSA-3w8g-xr3f-2mp8
CVE: CVE-2021-38190
CWE: CWE-119, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3w8g-xr3f-2mp8
Type: github-advisory

## Affected
- crates.io: `nalgebra` — affected >=0.11.0 <0.27.1

## Details
The `Deserialize` implementation for `VecStorage` did not maintain the invariant that the number of elements must equal `nrows * ncols`. Deserialization of specially crafted inputs could allow memory access beyond allocation of the vector.

This flaw was introduced in v0.11.0 ([`086e6e`](https://github.com/dimforge/nalgebra/commit/086e6e719f53fecba6dadad2e953a487976387f5)) due to the addition of an automatically derived implementation of `Deserialize` for `MatrixVec`. `MatrixVec` was later renamed to `VecStorage` in v0.16.13 ([`0f66403`](https://github.com/dimforge/nalgebra/commit/0f66403cbbe9eeac15cedd8a906c0d6a3d8841f2)) and continued to use the automatically derived implementation of `Deserialize`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38190
- https://github.com/dimforge/nalgebra/issues/883
- https://github.com/dimforge/nalgebra/pull/889
- https://github.com/dimforge/nalgebra/commit/a803271fcce75b7c151e92aa099dfa546db4adc5
- https://github.com/dimforge/nalgebra
- https://github.com/dimforge/nalgebra/blob/dev/CHANGELOG.md#0270
- https://rustsec.org/advisories/RUSTSEC-2021-0070.html
