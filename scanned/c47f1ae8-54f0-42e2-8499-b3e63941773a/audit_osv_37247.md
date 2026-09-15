# [C] CVE-2026-30269

## Summary
Severity: Critical
Advisory: CVE-2026-30269
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-30269
Type: osv

## Details
Improper access control in Doorman v0.1.0 and v1.0.2 allows any authenticated user to update their own account role to a non-admin privileged role via /platform/user/{username}. The `role` field is accepted by the update model without a manage_users permission check for self-updates, enabling privilege escalation to high-privileged roles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30269.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30269
- https://github.com/apidoorman/doorman
- https://blog.orxiain.life/archives/cve-2026-30269---improper-access-control-in-doorman-allows-privilege-escalation
