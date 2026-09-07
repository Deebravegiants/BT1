# [M] Multiple security issues including data race, buffer overflow, and uninitialized memory drop in arr

## Summary
Severity: Medium
Advisory: GHSA-c7fw-cr3w-wvfc
CVE: CVE-2020-35886
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c7fw-cr3w-wvfc
Type: github-advisory

## Affected
- crates.io: `arr` — affected >=0

## Details
arr crate contains multiple security issues. Specifically,

1.  It incorrectly implements Sync/Send bounds, which allows to smuggle non-Sync/Send types across the thread boundary.
2. Index and IndexMut implementation does not check the array bound.
3. Array::new_from_template() drops uninitialized memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35886
- https://github.com/sjep/array/issues/1
- https://github.com/sjep/array
- https://rustsec.org/advisories/RUSTSEC-2020-0034.html
