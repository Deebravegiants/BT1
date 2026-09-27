# [H] CVE-2017-18026

## Summary
Severity: High
Advisory: CVE-2017-18026
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-10
Source: https://osv.dev/vulnerability/CVE-2017-18026
Type: osv

## Details
Redmine before 3.2.9, 3.3.x before 3.3.6, and 3.4.x before 3.4.4 does not block the --config and --debugger flags to the Mercurial hg program, which allows remote attackers to execute arbitrary commands (through the Mercurial adapter) via vectors involving a branch whose name begins with a --config= or --debugger= substring, a related issue to CVE-2017-17536.

## References
- https://www.debian.org/security/2018/dsa-4191
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://www.redmine.org/issues/27516
- https://github.com/redmine/redmine/commit/58ed8655136ff2fe5ff7796859bf6a399c76c678
- https://github.com/redmine/redmine/commit/9d797400eaec5f9fa7ba9507c82d9c18cb91d02e
- https://github.com/redmine/redmine/commit/ca87bf766cdc70179cb2dce03015d78ec9c13ebd
