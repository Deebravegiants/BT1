# [M] CVE-2016-0704

## Summary
Severity: Medium
Advisory: CVE-2016-0704
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-03-02
Source: https://osv.dev/vulnerability/CVE-2016-0704
Type: osv

## Details
An oracle protection mechanism in the get_client_master_key function in s2_srvr.c in the SSLv2 implementation in OpenSSL before 0.9.8zf, 1.0.0 before 1.0.0r, 1.0.1 before 1.0.1m, and 1.0.2 before 1.0.2a overwrites incorrect MASTER-KEY bytes during use of export cipher suites, which makes it easier for remote attackers to decrypt TLS ciphertext data by leveraging a Bleichenbacher RSA padding oracle, a related issue to CVE-2016-0800.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160302-openssl
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/83764
- http://www.securitytracker.com/id/1035133
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
