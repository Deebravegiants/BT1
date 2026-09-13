# [C] CVE-2016-4024

## Summary
Severity: Critical
Advisory: CVE-2016-4024
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-4024
Type: osv

## Details
Integer overflow in imlib2 before 1.4.9 on 32-bit platforms allows remote attackers to execute arbitrary code via large dimensions in an image, which triggers an out-of-bounds heap memory write operation.

## References
- http://www.debian.org/security/2016/dsa-3555
- http://www.securityfocus.com/bid/86073
- http://www.securitytracker.com/id/1035573
- https://git.enlightenment.org/legacy/imlib2.git/commit/?id=7eba2e4c8ac0e20838947f10f29d0efe1add8227
- https://security.gentoo.org/glsa/201611-12
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00076.html
- https://sourceforge.net/p/enlightenment/mailman/message/35055012/
