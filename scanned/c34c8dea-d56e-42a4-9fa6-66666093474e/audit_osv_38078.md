# [M] iccDEV: UB at IccUtil.cpp

## Summary
Severity: Medium
Advisory: CVE-2026-34547
Aliases: GHSA-v8h6-8hxj-j7ff
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34547
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, an Undefined Behavior (UB) condition in IccUtil.cpp can be triggered by a crafted ICC profile when running iccDumpProfile. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34547.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-v8h6-8hxj-j7ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-34547
- https://github.com/InternationalColorConsortium/iccDEV/issues/720
- https://github.com/InternationalColorConsortium/iccDEV/pull/724
