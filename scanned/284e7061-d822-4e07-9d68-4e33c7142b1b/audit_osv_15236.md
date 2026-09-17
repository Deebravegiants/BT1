# [H] CVE-2019-14745

## Summary
Severity: High
Advisory: CVE-2019-14745
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2019-14745
Type: osv

## Details
In radare2 before 3.7.0, a command injection vulnerability exists in bin_symbols() in libr/core/cbin.c. By using a crafted executable file, it's possible to execute arbitrary shell commands with the permissions of the victim. This vulnerability is due to improper handling of symbol names embedded in executables.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ETWG4VKHWL5F74L3QBBKSCOXHSRNSRRT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MGA2PVBFA6VPWWLMBGWVBESHAJBQ7OXJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RQO7V37RGQEKZDLY2JYKDZTLNN2YUBC5/
- https://github.com/radare/radare2/releases/tag/3.7.0
- https://github.com/radare/radare2/pull/14690
- https://bananamafia.dev/post/r2-pwndebian/
