# [H] CVE-2018-19052

## Summary
Severity: High
Advisory: CVE-2018-19052
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19052
Type: osv

## Details
An issue was discovered in mod_alias_physical_handler in mod_alias.c in lighttpd before 1.4.50. There is potential ../ path traversal of a single directory above an alias target, with a specific mod_alias configuration where the matched alias lacks a trailing '/' character, but the alias target filesystem path does have a trailing '/' character.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00054.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00012.html
- https://github.com/lighttpd/lighttpd1.4/commit/2105dae0f9d7a964375ce681e53cb165375f84c1
