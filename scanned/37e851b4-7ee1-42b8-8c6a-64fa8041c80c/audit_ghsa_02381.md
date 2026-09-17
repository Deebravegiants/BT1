# [H] Use of Uninitialized Resource in ms3d

## Summary
Severity: High
Advisory: GHSA-9f5r-vqm5-m342
CVE: CVE-2021-26952
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9f5r-vqm5-m342
Type: github-advisory

## Affected
- crates.io: `ms3d` — affected >=0 <0.1.3

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation. Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

The flaw was fixed in commit `599313b` by zero-initializing the buffer (via self.buf.resize(len, 0)) before passing it to Read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26952
- https://github.com/andrewhickman/ms3d/issues/1
- https://github.com/andrewhickman/ms3d/commit/599313b
- https://github.com/andrewhickman/ms3d
- https://rustsec.org/advisories/RUSTSEC-2021-0016.html
