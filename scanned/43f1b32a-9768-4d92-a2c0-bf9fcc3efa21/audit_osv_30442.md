# [M] iTop portal Insecure Direct Object Reference vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-52601
Aliases: GHSA-cph2-466c-3f87
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2024-52601
Type: osv

## Details
iTop is an web based IT Service Management tool. Prior to versions 2.7.12, 3.1.3, and 3.2.1, anyone with an account having portal access can have read access to objects they're not allowed to see by querying an unprotected route. Versions 2.7.12, 3.1.3, and 3.2.1 contain a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52601.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-cph2-466c-3f87
- https://nvd.nist.gov/vuln/detail/CVE-2024-52601
