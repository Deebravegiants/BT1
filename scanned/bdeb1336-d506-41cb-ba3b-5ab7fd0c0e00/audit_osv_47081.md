# [H] CVE-2015-8899

## Summary
Severity: High
Advisory: CVE-2015-8899
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/CVE-2015-8899
Type: osv

## Details
Dnsmasq before 2.76 allows remote servers to cause a denial of service (crash) via a reply with an empty DNS address that has an (1) A or (2) AAAA record defined locally.

## References
- http://www.ubuntu.com/usn/USN-3009-1
- http://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2016q2/010479.html
- http://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2016q2/010505.html
- http://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=commit%3Bh=41a8d9e99be9f2cc8b02051dd322cb45e0faac87
- http://www.openwall.com/lists/oss-security/2016/06/03/7
- http://www.openwall.com/lists/oss-security/2016/06/04/2
- http://www.securityfocus.com/bid/91031
- http://www.securitytracker.com/id/1036045
