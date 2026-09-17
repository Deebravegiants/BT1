# [H] CVE-2017-14495

## Summary
Severity: High
Advisory: CVE-2017-14495
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-14495
Type: osv

## Details
Memory leak in dnsmasq before 2.78, when the --add-mac, --add-cpe-id or --add-subnet option is specified, allows remote attackers to cause a denial of service (memory consumption) via vectors involving DNS response creation.

## References
- http://nvidia.custhelp.com/app/answers/detail/a_id/4561
- http://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=commit%3Bh=51eadb692a5123b9838e5a68ecace3ac579a3a45
- http://www.arubanetworks.com/assets/alert/ARUBA-PSA-2017-005.txt
- http://www.securityfocus.com/bid/101977
- https://cert-portal.siemens.com/productcert/pdf/ssa-689071.pdf
- https://www.mail-archive.com/dnsmasq-discuss%40lists.thekelleys.org.uk/msg11664.html
- https://www.mail-archive.com/dnsmasq-discuss%40lists.thekelleys.org.uk/msg11665.html
- https://www.synology.com/support/security/Synology_SA_17_59_Dnsmasq
- http://thekelleys.org.uk/dnsmasq/CHANGELOG
- http://www.debian.org/security/2017/dsa-3989
- http://www.securityfocus.com/bid/101085
- http://www.securitytracker.com/id/1039474
- http://www.ubuntu.com/usn/USN-3430-1
- http://www.ubuntu.com/usn/USN-3430-2
- https://security.gentoo.org/glsa/201710-27
- https://security.googleblog.com/2017/10/behind-masq-yet-more-dns-and-dhcp.html
- https://www.exploit-db.com/exploits/42945/
- https://www.kb.cert.org/vuls/id/973527
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00006.html
- https://access.redhat.com/security/vulnerabilities/3199382
