# [M] CVE-2018-1071

## Summary
Severity: Medium
Advisory: CVE-2018-1071
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-1071
Type: osv

## Details
zsh through version 5.4.2 is vulnerable to a stack-based buffer overflow in the exec.c:hashcmd() function. A local attacker could exploit this to cause a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00000.html
- http://www.securityfocus.com/bid/103359
- https://access.redhat.com/errata/RHSA-2018:3073
- https://lists.debian.org/debian-lts-announce/2018/03/msg00038.html
- https://security.gentoo.org/glsa/201805-10
- https://usn.ubuntu.com/3608-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1553531
