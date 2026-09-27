# [H] Foreman: foreman: privilege escalation to administrator-level access via usergroup role assignment manipulation

## Summary
Severity: High
Advisory: CVE-2026-5136
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-5136
Type: osv

## Details
A flaw was found in Foreman. The Usergroup model in Foreman does not properly validate role assignments against the calling user's permissions. This allows an authenticated user with usergroup management permissions to attach arbitrary roles, including administrative roles, to a user group and then add themselves as a member. Successful exploitation of this vulnerability leads to full privilege escalation, granting the attacker administrator-level access.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:34365
- https://access.redhat.com/errata/RHSA-2026:34366
- https://access.redhat.com/errata/RHSA-2026:34367
- https://access.redhat.com/errata/RHSA-2026:34368
- https://access.redhat.com/security/cve/CVE-2026-5136
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5136
- https://bugzilla.redhat.com/show_bug.cgi?id=2452970
