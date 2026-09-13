# [C] Use of Uninitialized Resource in tectonic_xdv

## Summary
Severity: Critical
Advisory: GHSA-qwvx-c8j7-5g75
CVE: CVE-2021-45703
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-qwvx-c8j7-5g75
Type: github-advisory

## Affected
- crates.io: `tectonic_xdv` — affected >=0 <0.1.12

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation.

Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

The problem was fixed in commit `cdff034` by zero-initializing the buffer before passing it to a user-provided Read implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45703
- https://github.com/tectonic-typesetting/tectonic/issues/752
- https://github.com/tectonic-typesetting/tectonic/commit/cdff034e6d93cdfdafd13d8c6956e22fa5a57b79
- https://github.com/tectonic-typesetting/tectonic
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tectonic_xdv/RUSTSEC-2021-0112.md
- https://rustsec.org/advisories/RUSTSEC-2021-0112.html
