# [H] CVE-2026-57303

## Summary
Severity: High
Advisory: CVE-2026-57303
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57303
Type: osv

## Details
Jenkins Assembla Plugin 1.4 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks, allowing attackers able to control the responses of the configured Assembla server to extract secrets from the Jenkins controller or perform server-side request forgery.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3692%20(1)
