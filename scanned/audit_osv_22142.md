# [H] DayByDay CRM - Insufficient Session Expiration after Password Change

## Summary
Severity: High
Advisory: CVE-2022-22113
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2022-22113
Type: osv

## Details
In DayByDay CRM, versions 2.2.0 through 2.2.1 (latest) are vulnerable to Insufficient Session Expiration. When a password has been changed by the user or by an administrator, a user that was already logged in, will still have access to the application even after the password was changed.

## References
- https://github.com/Bottelet/DaybydayCRM/blob/master/config/session.php#L32
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/22xxx/CVE-2022-22113.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-22113
