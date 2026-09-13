# [M] NocoDB - Observable Discrepancy in the password-reset feature

## Summary
Severity: Medium
Advisory: CVE-2022-22120
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2022-22120
Type: osv

## Details
In NocoDB, versions 0.9 to 0.83.8 are vulnerable to Observable Discrepancy in the password-reset feature. When requesting a password reset for a given email address, the application displays an error message when the email isn't registered within the system. This allows attackers to enumerate the registered users' email addresses.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/22xxx/CVE-2022-22120.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-22120
- https://github.com/nocodb/nocodb/commit/f46e89b0
