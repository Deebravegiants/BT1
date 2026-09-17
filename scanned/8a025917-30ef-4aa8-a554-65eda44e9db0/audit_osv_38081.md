# [M] iccDEV: UB at IccIO.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-34550
Aliases: GHSA-rmxp-pxf4-p7wm
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34550
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is an Undefined Behavior (UB) condition in IccProfLib/IccIO.cpp caused by an implicit conversion from a negative signed integer to size_t (unsigned), which changes the value. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34550.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-rmxp-pxf4-p7wm
- https://nvd.nist.gov/vuln/detail/CVE-2026-34550
- https://github.com/InternationalColorConsortium/iccDEV/issues/718
- https://github.com/InternationalColorConsortium/iccDEV/pull/727
