# [M] iccDEV has Out-of-bounds Read, Use of Out-of-range Pointer Offset and Improper Input Validation

## Summary
Severity: Medium
Advisory: CVE-2026-21487
Aliases: GHSA-xq7x-9524-f7cp
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21487
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1.1 and below have an Out-of-bounds Read, Use of Out-of-range Pointer Offset and have Improper Input Validation in its CIccProfile::LoadTag function. This issue is fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21487.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-xq7x-9524-f7cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-21487
- https://github.com/InternationalColorConsortium/iccDEV/issues/340
- https://github.com/InternationalColorConsortium/iccDEV/commit/1516e2cafc253bb06fd3700d589a4ed0f09f7bd6
