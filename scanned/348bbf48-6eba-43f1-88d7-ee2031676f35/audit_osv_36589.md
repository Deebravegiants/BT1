# [M] Admin RCE via Malicious Plugin Upload on CI Test Instances

## Summary
Severity: Medium
Advisory: CVE-2026-2462
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-2462
Type: osv

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to restrict plugin installation on CI test instances with default admin credentials which allows an unauthenticated attacker to achieve remote code execution and exfiltrate sensitive configuration data including AWS and SMTP credentials via uploading a malicious plugin after changing the import directory. Mattermost Advisory ID: MMSA-2025-00528

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2462.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-2462
