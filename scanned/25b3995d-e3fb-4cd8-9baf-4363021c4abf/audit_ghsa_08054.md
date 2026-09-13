# [H] PyO3 has type confusion when accessing data from sublasses of subclasses of native types with `abi3` feature

## Summary
Severity: High
Advisory: GHSA-47qc-857f-7w7f
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-47qc-857f-7w7f
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0.28.0 <0.28.2

## Details
PyO3 0.28.1 added support for `#[pyclass(extends=PyList)] struct NativeSub` (and other native types) when targeting Python 3.12 and up with the `abi3` feature.

It was discovered that subclasses of such classes would use the type of the subclass when attempting to access to data of `NativeSub` contained within Python objects, amounting to memory corruption.

PyO3 0.28.2 fixed the issue by using the type of (e.g.) `NativeSub` correctly.

## References
- https://github.com/PyO3/pyo3/pull/5807#issuecomment-3913251784
- https://github.com/PyO3/pyo3/commit/75abd8602896b350fd8c778e52e0a74b4644ccca
- https://github.com/PyO3/pyo3
- https://github.com/PyO3/pyo3/releases/tag/v0.28.2
- https://rustsec.org/advisories/RUSTSEC-2026-0013.html
