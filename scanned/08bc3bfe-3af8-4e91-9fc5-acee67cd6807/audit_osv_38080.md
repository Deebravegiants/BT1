# [M] iccDEV: UB at IccUtil.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-34549
Aliases: GHSA-v7qh-f995-p2fq
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34549
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, there is an Undefined Behavior (UB) condition in IccUtil.cpp triggered by a crafted input profile. Under UndefinedBehaviorSanitizer, the issue is reported as invalid left shift operations on icUInt32Number (unsigned 32-bit) where the shifted value “cannot be represented” in that type. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34549.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-v7qh-f995-p2fq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34549
- https://github.com/InternationalColorConsortium/iccDEV/issues/721
- https://github.com/InternationalColorConsortium/iccDEV/pull/726
