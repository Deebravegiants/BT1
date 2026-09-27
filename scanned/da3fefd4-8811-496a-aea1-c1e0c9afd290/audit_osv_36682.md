# [C] Budibase Critical Privilege Escalation & IDOR via Missing RBAC on User Role Management (Creator-Role)

## Summary
Severity: Critical
Advisory: CVE-2026-25045
Aliases: GHSA-2g39-332f-68p9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-25045
Type: osv

## Details
Budibase is a low code platform for creating internal tools, workflows, and admin panels. This issue is a combination of Vertical Privilege Escalation and IDOR (Insecure Direct Object Reference) due to missing server-side RBAC checks in the /api/global/users endpoints. A Creator-level user, who should have no permissions to manage users or organizational roles, can instead promote an App Viewer to Tenant Admin, demote a Tenant Admin to App Viewer, or modify the Owner’s account details and all orders (e.g., change name). This is because the API accepts these actions without validating the requesting role, a Creator can replay Owner-only requests using their own session tokens. This leads to full tenant compromise.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-2g39-332f-68p9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25045.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25045
