# [M] CVE-2026-57302

## Summary
Severity: Medium
Advisory: CVE-2026-57302
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57302
Type: osv

## Details
Jenkins FitNesse Plugin 1.36 and earlier stores passwords unencrypted in job config.xml files on the Jenkins controller, where they can be viewed by users with Extended Read permission or access to the Jenkins controller file system.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3555
