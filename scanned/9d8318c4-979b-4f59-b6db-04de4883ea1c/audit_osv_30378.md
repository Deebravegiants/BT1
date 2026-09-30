# [M] SSRF through arbitrary PHP class instantiation in the user portal in Combodo iTop

## Summary
Severity: Medium
Advisory: CVE-2024-51740
Aliases: GHSA-w9g8-mxm5-ph62
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-51740
Type: osv

## Details
Combodo iTop is a simple, web based IT Service Management tool. This vulnerability can be used to create HTTP requests on behalf of the server, from a low privileged user. The user portal form manager has been fixed to only instantiate classes derived from it. This issue has been addressed in versions 2.7.11, 3.0.5, 3.1.2, and 3.2.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51740.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-w9g8-mxm5-ph62
- https://nvd.nist.gov/vuln/detail/CVE-2024-51740
