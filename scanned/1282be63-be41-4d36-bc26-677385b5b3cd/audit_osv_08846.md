# [H] CVE-2016-6318

## Summary
Severity: High
Advisory: CVE-2016-6318
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/CVE-2016-6318
Type: osv

## Details
Stack-based buffer overflow in the FascistGecosUser function in lib/fascist.c in cracklib allows local users to cause a denial of service (application crash) or gain privileges via a long GECOS field, involving longbuffer.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00122.html
- http://www.openwall.com/lists/oss-security/2016/08/16/2
- http://www.securityfocus.com/bid/92478
- https://lists.debian.org/debian-lts-announce/2020/05/msg00023.html
- https://security.gentoo.org/glsa/201612-25
