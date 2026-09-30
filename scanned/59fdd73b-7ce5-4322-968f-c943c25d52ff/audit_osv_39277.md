# [C] Cross-Cluster Impersonation Confused-Deputy Privilege Escalation

## Summary
Severity: Critical
Advisory: CVE-2026-44945
Aliases: GHSA-v584-7w32-jwpq
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-44945
Type: osv

## Details
A privilege escalation vulnerability exists in Rancher's impersonation middleware (pkg/auth/requests/impersonate.go). An authenticated Rancher user with the default user
 global role can gain full administrative access to the Rancher control 
plane and transitively to all downstream clusters it manages.

This issue affects Rancher: from 2.11.0 before 2.11.16, from 2.12.0 before 2.12.12, from 2.13.0 before 2.13.8, and from 2.14.0 before 2.14.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44945.json
- https://github.com/rancher/rancher/security/advisories/GHSA-v584-7w32-jwpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44945
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-44945
- https://github.com/rancher/rancher/pull/55983
- https://github.com/rancher/rancher
