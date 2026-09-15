# [M] CVE-2015-8473

## Summary
Severity: Medium
Advisory: CVE-2015-8473
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2015-8473
Type: osv

## Details
The Issues API in Redmine before 2.6.8, 3.0.x before 3.0.6, and 3.1.x before 3.1.2 allows remote authenticated users to obtain sensitive information in changeset messages by leveraging permission to read issues with related changesets from other projects.

## References
- http://www.debian.org/security/2016/dsa-3529
- https://www.redmine.org/versions/105
- https://github.com/redmine/redmine/commit/8d8f612fa368a72c56b63f7ce6b7e98cab9feb22
- https://www.redmine.org/issues/21136
- https://www.redmine.org/projects/redmine/wiki/Changelog_3_0
- https://www.redmine.org/projects/redmine/wiki/Changelog_3_1
- https://www.redmine.org/versions/105
- http://www.securityfocus.com/bid/78621
