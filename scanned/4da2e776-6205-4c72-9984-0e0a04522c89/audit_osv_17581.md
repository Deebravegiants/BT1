# [C] CVE-2020-17353

## Summary
Severity: Critical
Advisory: CVE-2020-17353
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/CVE-2020-17353
Type: osv

## Details
scm/define-stencil-commands.scm in LilyPond through 2.20.0, and 2.21.x through 2.21.4, when -dsafe is used, lacks restrictions on embedded-ps and embedded-svg, as demonstrated by including dangerous PostScript code.

## References
- http://git.savannah.gnu.org/gitweb/?p=lilypond.git%3Ba=commit%3Bh=b84ea4740f3279516905c5db05f4074e777c16ff
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QG2JUV4UTIA27JUE6IZLCEFP5PYSFPF4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W2JYMVLTPSNYS5F7TBHKIXUZZJIJAMRX/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00076.html
- https://www.debian.org/security/2020/dsa-4756
