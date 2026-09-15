# [M] Combodo iTop vulnerable to IDOR with ModuleInstallation object

## Summary
Severity: Medium
Advisory: CVE-2025-48878
Aliases: GHSA-rj75-7cgw-4556
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-11-10
Source: https://osv.dev/vulnerability/CVE-2025-48878
Type: osv

## Details
Combodo iTop is a web based IT service management tool. In versions on the 3.x branch prior to 3.2.2, an insecure direct object reference allows a user (e.g. with Service desk agent profile) to create a ModuleInstallation object when they shouldn't be able to do so. Version 3.2.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48878.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-rj75-7cgw-4556
- https://nvd.nist.gov/vuln/detail/CVE-2025-48878
