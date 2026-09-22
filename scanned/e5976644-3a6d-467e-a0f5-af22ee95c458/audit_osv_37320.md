# [M] iccDEV has a stack overflow in CIccBasicStructFactory::CreateStruct()

## Summary
Severity: Medium
Advisory: CVE-2026-30980
Aliases: GHSA-w478-77q7-2hc2
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-30980
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a stack overflow in CIccBasicStructFactory::CreateStruct() causing uncontrolled recursion/stack exhaustion and crash. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30980.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-w478-77q7-2hc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-30980
- https://github.com/InternationalColorConsortium/iccDEV/issues/629
- https://github.com/InternationalColorConsortium/iccDEV/pull/630
