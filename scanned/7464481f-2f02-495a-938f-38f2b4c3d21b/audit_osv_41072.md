# [M] CVE-2026-57286

## Summary
Severity: Medium
Advisory: CVE-2026-57286
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57286
Type: osv

## Details
A missing permission check in Jenkins Git Parameter Plugin 462.vdcf3df2ed2ca_ and earlier allows attackers with Item/Read permission to obtain information about the SCM repository used by a job, such as branch names, tag names, and revision metadata.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3745
