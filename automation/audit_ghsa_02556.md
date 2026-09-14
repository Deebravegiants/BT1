# [M] Unexpected panic when decoding tokens in branca

## Summary
Severity: Medium
Advisory: GHSA-c9rv-3jmq-527w
CVE: CVE-2020-35918
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c9rv-3jmq-527w
Type: github-advisory

## Affected
- crates.io: `branca` — affected >=0 <0.10.0

## Details
Prior to 0.10.0 it was possible to have both decoding functions panic unexpectedly, by supplying tokens with an incorrect base62 encoding.
The documentation stated that an error should have been reported instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35918
- https://github.com/return/branca/issues/24
- https://github.com/tuupola/branca-spec/issues/22
- https://github.com/return/branca/commit/7da3274bd99b05dce9c3f9b4b129d0145c71820b
- https://github.com/return/branca
- https://rustsec.org/advisories/RUSTSEC-2020-0075.html
