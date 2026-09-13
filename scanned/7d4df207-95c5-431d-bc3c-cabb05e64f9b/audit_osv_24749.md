# [H] ZoneMinder contains SQL injection via malicious Jason Web Token

## Summary
Severity: High
Advisory: CVE-2023-26032
Aliases: GHSA-6c72-q9mw-mwx9
CVSS: 8.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26032
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 contain SQL Injection via malicious jason web token. The Username field of the JWT token was trusted when performing an SQL query to load the user.  If an attacker could determine the HASH key used by ZoneMinder, they could generate a malicious JWT token and use it to execute arbitrary SQL. This issue is fixed in versions 1.36.33 and 1.37.33.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26032.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-6c72-q9mw-mwx9
- https://nvd.nist.gov/vuln/detail/CVE-2023-26032
