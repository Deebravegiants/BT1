# [H] CVE-2017-15238

## Summary
Severity: High
Advisory: CVE-2017-15238
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-15238
Type: osv

## Details
ReadOneJNGImage in coders/png.c in GraphicsMagick 1.3.26 has a use-after-free issue when the height or width is zero, related to ReadJNGImage.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=93bdb9b30076
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=df946910910d
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://www.debian.org/security/2018/dsa-4321
- https://sourceforge.net/p/graphicsmagick/bugs/469/
