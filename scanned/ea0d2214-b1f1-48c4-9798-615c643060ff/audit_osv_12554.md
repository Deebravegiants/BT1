# [H] CVE-2018-1289

## Summary
Severity: High
Advisory: CVE-2018-1289
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2018-1289
Type: osv

## Details
In Apache Fineract versions 1.0.0, 0.6.0-incubating, 0.5.0-incubating, 0.4.0-incubating, the system exposes different REST end points to query domain specific entities with a Query Parameter 'orderBy' and 'sortOrder' which are appended directly with SQL statements. A hacker/user can inject/draft the 'orderBy' and 'sortOrder' query parameter in such a way to read/update the data for which he doesn't have authorization.

## References
- https://lists.apache.org/thread.html/4a1312b18ed2979fba9e2df07839e6a940eeeea12ed9154db1a49a5a%40%3Cdev.fineract.apache.org%3E
- http://www.securityfocus.com/bid/104005
