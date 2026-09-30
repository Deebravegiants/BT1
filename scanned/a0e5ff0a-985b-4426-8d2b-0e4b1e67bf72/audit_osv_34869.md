# [C] WBCE CMS is Vulnerable to Time-Based Blind SQL Injection through groups[] Parameter

## Summary
Severity: Critical
Advisory: CVE-2025-65950
Aliases: GHSA-934v-xhx9-j2f3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2025-65950
Type: osv

## Details
WBCE CMS is a content management system. In versions 1.6.4 and below, the user management module allows a low-privileged authenticated user with permissions to modify users to execute arbitrary SQL queries. This can be escalated to a full database compromise, data exfiltration, effectively bypassing all security controls. The vulnerability exists in the admin/users/save.php script, which handles updates to user profiles. The script improperly processes the groups[] parameter sent from the user edit form. This issue is fixed in version 1.6.5.

## References
- https://github.com/WBCE/WBCE_CMS/releases/tag/1.6.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65950.json
- https://github.com/WBCE/WBCE_CMS/security/advisories/GHSA-934v-xhx9-j2f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-65950
- https://github.com/WBCE/WBCE_CMS/commit/96046178f4c80cf16f7c224054dec7fdadddda7e
