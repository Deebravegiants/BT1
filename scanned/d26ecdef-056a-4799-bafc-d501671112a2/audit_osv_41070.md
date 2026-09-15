# [M] CVE-2026-57284

## Summary
Severity: Medium
Advisory: CVE-2026-57284
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57284
Type: osv

## Details
Jenkins Pipeline: Groovy Plugin 4331.v9d06ed4658ff and earlier does not restrict the types that can be instantiated through the Pipeline Snippet Generator, allowing attackers to instantiate types related to job or system configuration other than Pipeline steps.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3677
