# [M] Uninitialized memory exposure in claxon

## Summary
Severity: Medium
Advisory: GHSA-8c6g-4xc5-w96c
CVE: CVE-2018-20992
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8c6g-4xc5-w96c
Type: github-advisory

## Affected
- crates.io: `claxon` — affected >=0.4.0 <0.4.1
- crates.io: `claxon` — affected >=0 <0.3.2

## Details
Affected versions of Claxon made an invalid assumption about the decode buffer size being a multiple of a value read from the bitstream. This could cause parts of the decode buffer to not be overwritten. If the decode buffer was newly allocated and uninitialized, this uninitialized memory could be exposed.

This allows an attacker to observe parts of the uninitialized memory in the decoded audio stream.

The flaw was corrected by checking that the value read from the bitstream divides the decode buffer size, and returning a format error if it does not. If an error is returned, the decode buffer is not exposed. Regression tests and an additional fuzzer have been added to prevent similar flaws in the future.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20992
- https://github.com/ruuda/claxon/commit/8f28ec275e412dd3af4f3cda460605512faf332c
- https://github.com/ruuda/claxon
- https://github.com/ruuda/claxon/releases/tag/v0.3.2
- https://github.com/ruuda/claxon/releases/tag/v0.4.1
- https://rustsec.org/advisories/RUSTSEC-2018-0004.html
