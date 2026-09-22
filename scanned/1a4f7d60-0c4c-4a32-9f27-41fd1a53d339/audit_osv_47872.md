# [M] CVE-2017-14121

## Summary
Severity: Medium
Advisory: CVE-2017-14121
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-03
Source: https://osv.dev/vulnerability/CVE-2017-14121
Type: osv

## Details
The DecodeNumber function in unrarlib.c in unrar 0.0.1 (aka unrar-free or unrar-gpl) suffers from a NULL pointer dereference flaw triggered by a crafted RAR archive. NOTE: this may be the same as one of the several test cases in the CVE-2017-11189 references.

## References
- http://www.openwall.com/lists/oss-security/2017/08/20/1
- https://lists.debian.org/debian-lts-announce/2021/02/msg00026.html
- https://bugs.debian.org/874061
