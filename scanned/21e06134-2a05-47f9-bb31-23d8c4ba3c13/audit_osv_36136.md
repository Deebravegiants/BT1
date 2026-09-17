# [M] NULL Pointer Dereference in iccDEV XML Calculator Parser

## Summary
Severity: Medium
Advisory: CVE-2026-21498
Aliases: GHSA-6822-qvxq-m736
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21498
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to NULL pointer dereference via the XML calculator parser. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21498.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-6822-qvxq-m736
- https://nvd.nist.gov/vuln/detail/CVE-2026-21498
- https://github.com/InternationalColorConsortium/iccDEV/issues/375
- https://github.com/InternationalColorConsortium/iccDEV/commit/75f124f40ba45491211cb4b67f0e05b7c7d59553
- https://github.com/InternationalColorConsortium/iccDEV/commit/bdfa31940726aaabb0a6f19194d9062ba0598959
- https://github.com/InternationalColorConsortium/iccDEV/pull/404
