# [H] iccDEV Undefined Behavior (UB) and Out of Memory in CIccProfile::LoadTag()

## Summary
Severity: High
Advisory: CVE-2026-21485
Aliases: GHSA-chp2-4gv5-2432
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21485
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1.1 and below are prone to have Undefined Behavior (UB) and Out of Memory errors. This issue is fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21485.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-chp2-4gv5-2432
- https://nvd.nist.gov/vuln/detail/CVE-2026-21485
- https://github.com/InternationalColorConsortium/iccDEV/issues/340
- https://github.com/InternationalColorConsortium/iccDEV/commit/c136aac51d25cbb4d9db63f071edad4f088843df
