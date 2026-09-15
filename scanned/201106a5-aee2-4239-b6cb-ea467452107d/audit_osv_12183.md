# [H] CVE-2018-1083

## Summary
Severity: High
Advisory: CVE-2018-1083
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-28
Source: https://osv.dev/vulnerability/CVE-2018-1083
Type: osv

## Details
Zsh before version 5.4.2-test-1 is vulnerable to a buffer overflow in the shell autocomplete functionality. A local unprivileged user can create a specially crafted directory path which leads to code execution in the context of the user who tries to use autocomplete to traverse the before mentioned path. If the user affected is privileged, this leads to privilege escalation.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00000.html
- http://www.securityfocus.com/bid/103572
- https://access.redhat.com/errata/RHSA-2018:1932
- https://access.redhat.com/errata/RHSA-2018:3073
- https://lists.debian.org/debian-lts-announce/2018/03/msg00038.html
- https://security.gentoo.org/glsa/201805-10
- https://usn.ubuntu.com/3608-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1557382
- https://sourceforge.net/p/zsh/code/ci/259ac472eac291c8c103c7a0d8a4eaf3c2942ed7
