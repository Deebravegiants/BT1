# [M] Element allows a malicious homeserver can modify events leading to unrenderable events or rooms

## Summary
Severity: Medium
Advisory: CVE-2024-51750
Aliases: GHSA-w36j-v56h-q9pc
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-51750
Type: osv

## Details
Element is a Matrix web client built using the Matrix React SDK. A malicious homeserver can send invalid messages over federation which can prevent Element Web and Desktop from rendering single messages or the entire room containing them. This was patched in Element Web and Desktop 1.11.85.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51750.json
- https://github.com/element-hq/element-web/security/advisories/GHSA-w36j-v56h-q9pc
- https://nvd.nist.gov/vuln/detail/CVE-2024-51750
- https://github.com/element-hq/element-web/commit/231073c578d5f92b33cde7aa2b0b9c5836b2dc48
