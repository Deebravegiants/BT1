# [H] CVE-2025-65780

## Summary
Severity: High
Advisory: CVE-2025-65780
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65780
Type: osv

## Details
An issue was discovered in Wekan The Open Source kanban board system up to version 18.15, fixed in 18.16. Authenticated users can update their entire user document (beyond profile fields), including orgs/teams and loginDisabled, due to missing server-side authorization checks; this enables privilege escalation and unauthorized access to other teams/orgs.

## References
- https://github.com/wekan/wekan/blob/main/CHANGELOG.md#v816-2025-11-02-wekan--release
- https://wekan.fi/hall-of-fame/spacebleed/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65780.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65780
- https://github.com/wekan/wekan/commit/f26d58201855e861bab1cd1fda4d62c664efdb81
- https://github.com/wekan/wekan
