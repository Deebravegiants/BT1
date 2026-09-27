# [C] Unauthenticated SQL Injection in dotCMS Publish Audit API

## Summary
Severity: Critical
Advisory: CVE-2026-8054
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-8054
Type: osv

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') in the Publish Audit API endpoints (/api/auditPublishing/get and /api/auditPublishing/getAll) in dotCMS Core 25.11.04-1 through 26.04.28-02 allows remote unauthenticated attackers to read, modify, or destroy arbitrary database content. The endpoints did not enforce authentication and accepted unsanitized input used in dynamically constructed SQL. The fix in dotCMS Core 26.04.28-03 requires an authenticated backend user with the publishing-queue portlet permission. LTS releases are not affected as the vulnerable code path was never backported.

## References
- https://dev.dotcms.com/docs/known-security-issues?issueNumber=SI-75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8054.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8054
- https://github.com/dotCMS/core/pull/35553
- https://github.com/dotCMS/core
