# [M] Database Credential Exposure in the Logs

## Summary
Severity: Medium
Advisory: CVE-2024-3165
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-04-01
Source: https://osv.dev/vulnerability/CVE-2024-3165
Type: osv

## Details
System->Maintenance-> Log Files in dotCMS dashboard is providing the username/password for database connections in the log output. Nevertheless, this is a moderate issue as it requires a backend admin as well as that dbs are locked down by environment.  

OWASP Top 10 - A05) Insecure Design

OWASP Top 10 - A05) Security Misconfiguration

OWASP Top 10 - A09) Security Logging and Monitoring Failure

## References
- https://www.dotcms.com/security/SI-70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3165.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3165
- https://github.com/dotCMS/core/issues/27910
- https://github.com/dotCMS/core/pull/28006
