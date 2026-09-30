# [H] CVE-2017-17536

## Summary
Severity: High
Advisory: CVE-2017-17536
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-11
Source: https://osv.dev/vulnerability/CVE-2017-17536
Type: osv

## Details
Phabricator before 2017-11-10 does not block the --config and --debugger flags to the Mercurial hg program, which allows remote attackers to execute arbitrary code by using the web UI to browse a branch whose name begins with a --config= or --debugger= substring.

## References
- https://hackerone.com/reports/288704
- https://secure.phabricator.com/T13012
