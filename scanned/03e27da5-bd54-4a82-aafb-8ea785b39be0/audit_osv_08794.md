# [M] CVE-2016-6170

## Summary
Severity: Medium
Advisory: CVE-2016-6170
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-07-06
Source: https://osv.dev/vulnerability/CVE-2016-6170
Type: osv

## Details
ISC BIND through 9.9.9-P1, 9.10.x through 9.10.4-P1, and 9.11.x through 9.11.0b1 allows primary DNS servers to cause a denial of service (secondary DNS server crash) via a large AXFR response, and possibly allows IXFR servers to cause a denial of service (IXFR client crash) via a large IXFR response and allows remote authenticated users to cause a denial of service (primary DNS server crash) via a large UPDATE message.

## References
- http://www.openwall.com/lists/oss-security/2016/07/06/3
- http://www.securityfocus.com/bid/91611
- http://www.securitytracker.com/id/1036241
- https://kb.isc.org/article/AA-01390
- https://kb.isc.org/article/AA-01390/169/CVE-2016-6170
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015058.html
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015073.html
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015075.html
- https://security.gentoo.org/glsa/201610-07
- https://bugzilla.redhat.com/show_bug.cgi?id=1353563
- https://github.com/sischkg/xfer-limit/blob/master/README.md
