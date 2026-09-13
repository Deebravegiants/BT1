# [H] CVE-2016-0798

## Summary
Severity: High
Advisory: CVE-2016-0798
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-03-03
Source: https://osv.dev/vulnerability/CVE-2016-0798
Type: osv

## Details
Memory leak in the SRP_VBASE_get_by_user implementation in OpenSSL 1.0.1 before 1.0.1s and 1.0.2 before 1.0.2g allows remote attackers to cause a denial of service (memory consumption) by providing an invalid username in a connection attempt, related to apps/s_server.c and crypto/srp/srp_vfy.c.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160302-openssl
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/83705
- http://www.securityfocus.com/bid/91787
- http://www.securitytracker.com/id/1035133
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=259b664f950c2ba66fbf4b0fe5281327904ead21
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03741en_us
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA40168
- https://www.openssl.org/news/secadv/20160301.txt
- http://openssl.org/news/secadv/20160301.txt
- http://www.debian.org/security/2016/dsa-3500
