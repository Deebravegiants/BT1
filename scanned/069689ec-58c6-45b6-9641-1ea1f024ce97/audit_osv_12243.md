# [H] CVE-2018-1100

## Summary
Severity: High
Advisory: CVE-2018-1100
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-11
Source: https://osv.dev/vulnerability/CVE-2018-1100
Type: osv

## Details
zsh through version 5.4.2 is vulnerable to a stack-based buffer overflow in the utils.c:checkmailpath function. A local attacker could exploit this to execute arbitrary code in the context of another user.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00000.html
- https://access.redhat.com/errata/RHSA-2018:1932
- https://access.redhat.com/errata/RHSA-2018:3073
- https://security.gentoo.org/glsa/201805-10
- https://usn.ubuntu.com/3764-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1563395
- https://sourceforge.net/p/zsh/code/ci/31f72205630687c1cef89347863aab355296a27f/
