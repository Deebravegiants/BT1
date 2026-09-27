# [H] CVE-2026-57301

## Summary
Severity: High
Advisory: CVE-2026-57301
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57301
Type: osv

## Details
Jenkins OWASP ZAP Plugin 1.0.7 and earlier performs build operations on the Jenkins controller rather than the assigned agent, allowing attackers with Item/Configure permission to execute arbitrary code on the Jenkins controller.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3649
