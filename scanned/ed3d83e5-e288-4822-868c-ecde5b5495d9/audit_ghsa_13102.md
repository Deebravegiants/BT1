# [M] Index out of bounds leading to crash

## Summary
Severity: Medium
Advisory: GHSA-xgmm-3vvr-6c8j
CVE: CVE-2023-36307
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-05
Source: https://github.com/advisories/GHSA-xgmm-3vvr-6c8j
Type: github-advisory

## Affected
- Go: `simonwaldherr.de/go/zplgfa` — affected >=0

## Details
ZPLGFA 1.1.1 allows attackers to cause a panic (because of an integer index out of range during a ConvertToGraphicField call) via an image of zero width. NOTE: it is unclear whether there are common use cases in which this panic could have any security consequence

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36307
- https://github.com/SimonWaldherr/zplgfa/pull/6
- https://github.com/SimonWaldherr/zplgfa/commit/c0d018ffa921cd2460b80f766b7969fbe63678fc
- https://github.com/SimonWaldherr/zplgfa
