# [M] Kanboard's privilege escalation via mass assignment in user invite registration allows any invited user to become admin

## Summary
Severity: Medium
Advisory: CVE-2026-29056
Aliases: GHSA-2jvj-q44v-6p3x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:N/SA:N/E:P)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-29056
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Prior to 1.2.51, Kanboard's user invite registration endpoint (`UserInviteController::register()`) accepts all POST parameters and passes them to `UserModel::create()` without filtering out the `role` field. An attacker who receives an invite link can inject `role=app-admin` in the registration form to create an administrator account. Version 1.2.51 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29056.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-2jvj-q44v-6p3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-29056
