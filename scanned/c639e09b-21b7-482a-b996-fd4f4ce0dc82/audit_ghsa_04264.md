# [H] PyO3 has an Out-of-bounds Read in `nth` / `nth_back` for `PyList` and `PyTuple` iterators

## Summary
Severity: High
Advisory: GHSA-36hh-v3qg-5jq4
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-36hh-v3qg-5jq4
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0 <0.29.0

## Details
PyO3 0.24.0 added optimized implementations of `Iterator::nth` and `DoubleEndedIterator::nth_back` for the `BoundListIterator` and `BoundTupleIterator` types. These implementations computed the target index using unchecked `usize` addition (`index + n`) before bounds-checking against the sequence length, then read the element via `get_item_unchecked`.

In `nth` methods, a sufficiently large `n` (combined with a non-zero internal index) could cause the addition to overflow and wrap around, producing a small "target index" that passed the bounds check and enabling reads at the front of the `list` or `tuple` of elements previously yielded by the iterator.

In `nth_back` methods, a sufficiently large `n` could cause underflow in a similar fashion, however would instead allow reads of arbitrary memory past the end of the `list` or `tuple` storage.

## References
- https://github.com/PyO3/pyo3/pull/6086
- https://github.com/PyO3/pyo3
- https://rustsec.org/advisories/RUSTSEC-2026-0176.html
