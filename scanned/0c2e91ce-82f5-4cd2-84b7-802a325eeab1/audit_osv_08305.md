# [H] CVE-2016-2176

## Summary
Severity: High
Advisory: CVE-2016-2176
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2176
Type: osv

## Details
The X509_NAME_oneline function in crypto/x509/x509_obj.c in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h allows remote attackers to obtain sensitive information from process stack memory or cause a denial of service (buffer over-read) via crafted EBCDIC ASN.1 data.

## References
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- http://packetstormsecurity.com/files/136912/Slackware-Security-Advisory-openssl-Updates.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160504-openssl
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/89746
- http://www.securityfocus.com/bid/91787
- http://www.securitytracker.com/id/1035721
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.542103
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=2919516136a4227d9e6d8f2fe66ef976aaf8c561
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03756en_us
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03765en_us
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA40202
- https://kc.mcafee.com/corporate/index?page=content&id=SB10160
- https://support.apple.com/HT206903
- https://www.tenable.com/security/tns-2016-18
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- https://bto.bluecoat.com/security-advisory/sa123
