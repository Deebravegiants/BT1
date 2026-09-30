# [M] iTop doesn't have mass assignment of fields in the portal form

## Summary
Severity: Medium
Advisory: CVE-2025-24021
Aliases: GHSA-c8hm-h9gv-8jpj
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-24021
Type: osv

## Details
iTop is an web based IT Service Management tool. Prior to versions 2.7.12, 3.1.3, and 3.2.1, anyone with an account having portal access can set value to object fields when they're not supposed to. Versions 2.7.12, 3.1.3, and 3.2.1 contain a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24021.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-c8hm-h9gv-8jpj
- https://nvd.nist.gov/vuln/detail/CVE-2025-24021
- https://github.com/Combodo/iTop/commit/44290db312901fc5918cc537c74561487fb3713b
