# [H] CVE-2022-4515

## Summary
Severity: High
Advisory: CVE-2022-4515
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-20
Source: https://osv.dev/vulnerability/CVE-2022-4515
Type: osv

## Details
A flaw was found in Exuberant Ctags in the way it handles the "-o" option. This option specifies the tag filename. A crafted tag filename specified in the command line or in the configuration file results in arbitrary command execution because the externalSortTags() in sort.c calls the system(3) function in an unsafe way.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00040.html
- https://sourceforge.net/p/ctags/code/HEAD/tree/tags/ctags-5.8/sort.c#l56
