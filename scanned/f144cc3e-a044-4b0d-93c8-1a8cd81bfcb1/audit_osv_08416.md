# [H] CVE-2016-3104

## Summary
Severity: High
Advisory: CVE-2016-3104
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-3104
Type: osv

## Details
mongod in MongoDB 2.6, when using 2.4-style users, and 2.4 allow remote attackers to cause a denial of service (memory consumption and process termination) by leveraging in-memory database representation when authenticating against a non-existent database.

## References
- http://www.securityfocus.com/bid/94929
- https://jira.mongodb.org/browse/SERVER-24378
- https://bugzilla.redhat.com/show_bug.cgi?id=1324496
