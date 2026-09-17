# [M] CVE-2024-3164

## Summary
Severity: Medium
Advisory: CVE-2024-3164
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-04-01
Source: https://osv.dev/vulnerability/CVE-2024-3164
Type: osv

## Details
In dotCMS dashboard, the Tools and Log Files tabs under System → Maintenance Portlet, which is and always has been an Admin portlet, is accessible to anyone with that portlet and not just to CMS Admins. Users that get site admin but not a system admin, should not have access to the System Maintenance → Tools portlet. This would share database username and password under Log Files and download DB Dump and other dotCMS Content under Tools. Nothing in the System → Maintenance should be displayed for users with site admin role. Only system admins must have access to System Maintenance.

OWASP Top 10 - A01) Broken Access Control

OWASP Top 10 - A04) Insecure Design

## References
- https://www.dotcms.com/security/SI-69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3164.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3164
- https://github.com/dotCMS/core/issues/27909
- https://github.com/dotCMS/core/pull/27912
