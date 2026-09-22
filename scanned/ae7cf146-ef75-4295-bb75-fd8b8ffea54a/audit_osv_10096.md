# [H] CVE-2017-13704

## Summary
Severity: High
Advisory: CVE-2017-13704
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-13704
Type: osv

## Details
In dnsmasq before 2.78, if the DNS packet size does not match the expected size, the size parameter in a memset call gets a negative value. As it is an unsigned value, memset ends up writing up to 0xffffffff zero's (0xffffffffffffffff in 64 bit platforms), making dnsmasq crash.

## References
- http://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=commit%3Bh=63437ffbb58837b214b4b92cb1c54bc5f3279928
- http://www.securityfocus.com/bid/101977
- https://cert-portal.siemens.com/productcert/pdf/ssa-689071.pdf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4TK6DWC53WSU6633EVZL7H4PCWBYHMHK/
- https://www.mail-archive.com/dnsmasq-discuss%40lists.thekelleys.org.uk/msg11664.html
- https://www.mail-archive.com/dnsmasq-discuss%40lists.thekelleys.org.uk/msg11665.html
- https://www.synology.com/support/security/Synology_SA_17_59_Dnsmasq
- http://thekelleys.org.uk/dnsmasq/CHANGELOG
- http://www.securityfocus.com/bid/101085
- http://www.securitytracker.com/id/1039474
- https://security.googleblog.com/2017/10/behind-masq-yet-more-dns-and-dhcp.html
- https://access.redhat.com/security/vulnerabilities/3199382
