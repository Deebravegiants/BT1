# [C] Off-by-one Error in v2fly/v2ray-core

## Summary
Severity: Critical
Advisory: GHSA-4cxw-hq44-r344
CVE: CVE-2021-4070
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-4cxw-hq44-r344
Type: github-advisory

## Affected
- Go: `github.com/v2fly/v2ray-core/v4` — affected >=0 <4.44.0
- Go: `github.com/v2fly/v2ray-core` — affected >=0

## Details
v2fly/v2ray-core prior to 4.44.0 is vulnerable to an off-by-one error. Indexing operations on arrays, slices, or strings should use an index at most one less than the length. If the index is checked for being less than or equal to the length (`<=`), instead of less than the length (`<`), the index could be out of bounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4070
- https://github.com/v2fly/v2ray-core/commit/c1af2bfd7aa59a4482aa7f6ec4b9208c1d350b5c
- https://github.com/v2fly/v2ray-core
- https://huntr.dev/bounties/8da19456-4d89-41ef-9781-a41efd6a1877
