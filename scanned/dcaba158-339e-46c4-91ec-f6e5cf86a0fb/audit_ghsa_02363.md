# [H] Uninitialized buffer use in marc

## Summary
Severity: High
Advisory: GHSA-3mf3-2gv9-h39j
CVE: CVE-2021-26308
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3mf3-2gv9-h39j
Type: github-advisory

## Affected
- crates.io: `marc` — affected >=0 <2.0.0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation. (Record::read()). Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior. This flaw was fixed in commit 6299af0 by zero-initializing the newly allocated memory (via data.resize(len, 0)) instead of exposing uninitialized memory (unsafe { data.set_len(len) }).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26308
- https://github.com/blackbeam/rust-marc/issues/7
- https://github.com/blackbeam/rust-marc/commit/6299af0
- https://github.com/blackbeam/rust-marc
- https://rustsec.org/advisories/RUSTSEC-2021-0014.html
