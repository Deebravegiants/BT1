# [H] CVE-2016-3994

## Summary
Severity: High
Advisory: CVE-2016-3994
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-3994
Type: osv

## Details
The GIF loader in imlib2 before 1.4.9 allows remote attackers to cause a denial of service (application crash) or obtain sensitive information via a crafted image, which triggers an out-of-bounds read.

## References
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00076.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=785369
- https://git.enlightenment.org/legacy/imlib2.git/commit/?id=37a96801663b7b4cd3fbe56cc0eb8b6a17e766a8
- http://www.debian.org/security/2016/dsa-3555
- https://sourceforge.net/p/enlightenment/mailman/message/35055012/
