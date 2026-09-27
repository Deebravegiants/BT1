# [M] Vim affected by Command injection via newline in glob()

## Summary
Severity: Medium
Advisory: CVE-2026-33412
Aliases: GHSA-w5jw-f54h-x46c
CVSS: 5.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33412
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0202, a command injection vulnerability exists in Vim's glob() function on Unix-like systems. By including a newline character (\n) in a pattern passed to glob(), an attacker may be able to execute arbitrary shell commands. This vulnerability depends on the user's 'shell' setting. This issue has been patched in version 9.2.0202.

## References
- http://www.openwall.com/lists/oss-security/2026/03/19/10
- https://github.com/vim/vim/releases/tag/v9.2.0202
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33412.json
- https://access.redhat.com/errata/RHSA-2026:10065
- https://access.redhat.com/errata/RHSA-2026:10097
- https://access.redhat.com/errata/RHSA-2026:11768
- https://access.redhat.com/errata/RHSA-2026:12274
- https://access.redhat.com/errata/RHSA-2026:14773
- https://access.redhat.com/errata/RHSA-2026:15087
- https://access.redhat.com/errata/RHSA-2026:16008
- https://access.redhat.com/errata/RHSA-2026:16009
- https://access.redhat.com/errata/RHSA-2026:16174
- https://access.redhat.com/errata/RHSA-2026:17596
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:6502
- https://access.redhat.com/errata/RHSA-2026:6539
- https://access.redhat.com/errata/RHSA-2026:6540
- https://access.redhat.com/errata/RHSA-2026:6617
- https://access.redhat.com/errata/RHSA-2026:6619
- https://access.redhat.com/errata/RHSA-2026:6620
