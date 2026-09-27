# [H] CVE-2019-2386

## Summary
Severity: High
Advisory: CVE-2019-2386
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-06
Source: https://osv.dev/vulnerability/CVE-2019-2386
Type: osv

## Details
After user deletion in MongoDB Server the improper invalidation of authorization sessions allows an authenticated user's session to persist and become conflated with new accounts, if those accounts reuse the names of deleted ones. This issue affects MongoDB Server v4.0 versions prior to 4.0.9; MongoDB Server v3.6 versions prior to 3.6.13 and MongoDB Server v3.4 versions prior to 3.4.22.

Workaround: 
After deleting one or more users, restart any nodes which may have had active user authorization sessions.

Refrain from creating user accounts with the same name as previously deleted accounts.

## References
- https://jira.mongodb.org/browse/SERVER-38984
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0829
