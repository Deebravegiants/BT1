# [M] CVE-2015-1793

## Summary
Severity: Medium
Advisory: CVE-2015-1793
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2015-07-09
Source: https://osv.dev/vulnerability/CVE-2015-1793
Type: osv

## Details
The X509_verify_cert function in crypto/x509/x509_vfy.c in OpenSSL 1.0.1n, 1.0.1o, 1.0.2b, and 1.0.2c does not properly process X.509 Basic Constraints cA values during identification of alternative certificate chains, which allows remote attackers to spoof a Certification Authority role and trigger unintended certificate verifications via a valid leaf certificate.

## References
- http://fortiguard.com/advisory/2015-07-09-cve-2015-1793-openssl-alternative-chains-certificate-forgery
- http://ftp.netbsd.org/pub/NetBSD/security/advisories/NetBSD-SA2015-008.txt.asc
- http://openssl.org/news/secadv_20150709.txt
- http://www.fortiguard.com/advisory/2015-07-09-cve-2015-1793-openssl-alternative-chains-certificate-forgery
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www1.huawei.com/en/security/psirt/security-bulletins/security-advisories/hw-454058.htm
- https://security.gentoo.org/glsa/201507-15
- https://www.freebsd.org/security/advisories/FreeBSD-SA-15:12.openssl.asc
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/topics/security/cpujan2016-2367955.html
- http://www.oracle.com/technetwork/topics/security/cpuoct2015-2367953.html
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10694
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161747.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161782.html
- http://marc.info/?l=bugtraq&m=143880121627664&w=2
- http://marc.info/?l=bugtraq&m=144370846326989&w=2
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20150710-openssl
- http://www.oracle.com/technetwork/topics/security/bulletinjul2015-2511963.html
