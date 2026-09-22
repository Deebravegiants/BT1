# [H] Read on uninitialized buffer in postscript

## Summary
Severity: High
Advisory: GHSA-fhvc-gp6c-h2wx
CVE: CVE-2021-26953
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fhvc-gp6c-h2wx
Type: github-advisory

## Affected
- crates.io: `postscript` — affected >=0 <0.14.0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation.

Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

This flaw was fixed in commit `8026286` by zero-initializing the buffer before handing to a user-provided Read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26953
- https://github.com/bodoni/postscript/issues/1
- https://github.com/bodoni/postscript/commit/8026286
- https://github.com/bodoni/postscript
- https://rustsec.org/advisories/RUSTSEC-2021-0017.html
