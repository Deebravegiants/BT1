# [H] CVE-2018-20683

## Summary
Severity: High
Advisory: CVE-2018-20683
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2018-20683
Type: osv

## Details
commands/rsync in Gitolite before 3.6.11, if .gitolite.rc enables rsync, mishandles the rsync command line, which allows attackers to have a "bad" impact by triggering use of an option other than -v, -n, -q, or -P.

## References
- https://groups.google.com/forum/#%21topic/gitolite-announce/6xbjjmpLePQ
- https://github.com/sitaramc/gitolite/blob/master/CHANGELOG
- https://bugs.debian.org/918849
- https://github.com/sitaramc/gitolite/commit/5df2b817255ee919991da6c310239e08c8fcc1ae
