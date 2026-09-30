# [C] ZoneMinder SQL Injection

## Summary
Severity: Critical
Advisory: CVE-2023-26034
Aliases: GHSA-222j-wh8m-xjrx
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26034
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 are affected by a SQL Injection vulnerability. The (blind) SQL Injection vulnerability is present within the `filter[Query][terms][0][attr]` query string parameter of the  `/zm/index.php` endpoint. A user with the View or Edit permissions of Events may execute arbitrary SQL. The resulting impact can include unauthorized data access (and modification), authentication and/or authorization bypass, and remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26034.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-222j-wh8m-xjrx
- https://nvd.nist.gov/vuln/detail/CVE-2023-26034
