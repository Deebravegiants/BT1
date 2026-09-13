# [M] Galette has a privilege escalation vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-58053
Aliases: GHSA-r7x8-6r56-498r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-58053
Type: osv

## Details
Galette is a membership management web application for non profit organizations. Prior to version 1.2.0, while updating any existing account with a self forged POST request, one can gain higher privileges. Version 1.2.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58053.json
- https://github.com/galette/galette/security/advisories/GHSA-r7x8-6r56-498r
- https://nvd.nist.gov/vuln/detail/CVE-2025-58053
