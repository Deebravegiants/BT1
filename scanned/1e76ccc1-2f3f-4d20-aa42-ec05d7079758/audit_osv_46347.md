# [H] CVE-2004-0079

## Summary
Severity: High
Advisory: CVE-2004-0079
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2004-11-23
Source: https://osv.dev/vulnerability/CVE-2004-0079
Type: osv

## Details
The do_change_cipher_spec function in OpenSSL 0.9.6c to 0.9.6k, and 0.9.7a to 0.9.7c, allows remote attackers to cause a denial of service (crash) via a crafted SSL/TLS handshake that triggers a null dereference.

## References
- ftp://ftp.freebsd.org/pub/FreeBSD/CERT/advisories/FreeBSD-SA-04:05.openssl.asc
- ftp://ftp.netbsd.org/pub/NetBSD/security/advisories/NetBSD-SA2004-005.txt.asc
- http://fedoranews.org/updates/FEDORA-2004-095.shtml
- http://secunia.com/advisories/11139
- http://secunia.com/advisories/17381
- http://secunia.com/advisories/17398
- http://secunia.com/advisories/17401
- http://secunia.com/advisories/18247
- http://security.gentoo.org/glsa/glsa-200403-03.xml
- http://support.avaya.com/elmodocs2/security/ASA-2005-239.htm
- http://www.debian.org/security/2004/dsa-465
- http://www.kb.cert.org/vuls/id/288574
- http://www.linuxsecurity.com/advisories/engarde_advisory-4135.html
- http://www.mandriva.com/security/advisories?name=MDKSA-2004:023
- http://www.novell.com/linux/security/advisories/2004_07_openssl.html
- http://www.openssl.org/news/secadv_20040317.txt
- http://www.securityfocus.com/bid/9899
- http://www.us-cert.gov/cas/techalerts/TA04-078A.html
- https://exchange.xforce.ibmcloud.com/vulnerabilities/15505
- http://lists.apple.com/archives/security-announce/2005//Aug/msg00001.html
