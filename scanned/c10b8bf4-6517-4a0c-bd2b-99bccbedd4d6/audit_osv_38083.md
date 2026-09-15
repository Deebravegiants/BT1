# [M] iccDEV: UB at IccTagLut.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-34552
Aliases: GHSA-wgh5-wvv2-r8pq
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34552
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is an Undefined Behavior (UB) issue in IccTagLut.cpp where the code performs member access through a null pointer of type CIccApplyCLUT. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34552.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-wgh5-wvv2-r8pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34552
- https://github.com/InternationalColorConsortium/iccDEV/issues/701
- https://github.com/InternationalColorConsortium/iccDEV/pull/730
