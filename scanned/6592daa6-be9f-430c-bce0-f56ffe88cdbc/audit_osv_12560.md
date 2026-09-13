# [H] CVE-2018-1291

## Summary
Severity: High
Advisory: CVE-2018-1291
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2018-1291
Type: osv

## Details
Apache Fineract 1.0.0, 0.6.0-incubating, 0.5.0-incubating, 0.4.0-incubating exposes different REST end points to query domain specific entities with a Query Parameter 'orderBy' which are appended directly with SQL statements. A hacker/user can inject/draft the 'orderBy' query parameter by way of the "order" param in such a way to read/update the data for which he doesn't have authorization.

## References
- https://lists.apache.org/thread.html/1f7fadc93500b3fe14603b132b13c18fff3d0a35e50ebd0246f325c0%40%3Cdev.fineract.apache.org%3E
- http://www.securityfocus.com/bid/104008
