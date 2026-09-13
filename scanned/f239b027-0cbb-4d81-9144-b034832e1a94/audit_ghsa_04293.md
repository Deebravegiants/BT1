# [M] PyO3 has a missing `Sync` bound on `PyCFunction::new_closure` closures

## Summary
Severity: Medium
Advisory: GHSA-chgr-c6px-7xpp
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-chgr-c6px-7xpp
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0 <0.29.0

## Details
`PyCFunction::new_closure` (and the temporary `new_closure_bound` complement in the 0.21–0.22 series) required the supplied closure to be `Send + 'static` but not `Sync`. The resulting `PyCFunction` is a Python callable that can be invoked from any Python thread, which means the closure may be called concurrently from multiple threads, and needs a `Sync` bound to prevent possible data races.

The problem exists under all Python versions but is particularly vulnerable under the newer free-threaded Python variant, which do not have serial execution imposed by the Global Interpreter Lock. Under releases protected by the GIL, the ability to "detach" from the Python interpreter temporarily inside the closure (e.g. by `Python::detach`) makes it possible for interleaved and/or concurrent execution of various portions of the closure.

PyO3 0.29.0 added a `Sync` bound to close this thread-safety bug.

## References
- https://github.com/PyO3/pyo3/pull/6096
- https://github.com/PyO3/pyo3
- https://github.com/PyO3/pyo3/releases/tag/v0.29.0
- https://rustsec.org/advisories/RUSTSEC-2026-0177.html
