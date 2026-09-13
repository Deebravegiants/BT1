# [H] CVE-2018-16976

## Summary
Severity: High
Advisory: CVE-2018-16976
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-09-12
Source: https://osv.dev/vulnerability/CVE-2018-16976
Type: osv

## Details
Gitolite before 3.6.9 does not (in certain configurations involving @all or a regex) properly restrict access to a Git repository that is in the process of being migrated until the full set of migration steps has been completed. This can allow valid users to obtain unintended access.

## References
- https://groups.google.com/forum/#%21topic/gitolite-announce/WrwDTYdbfRg
- https://bugs.debian.org/908699
- https://github.com/sitaramc/gitolite/commit/dc13dfca8fdae5634bb0865f7e9822d2a268ed59
