# [M] CVE-2015-3195

## Summary
Severity: Medium
Advisory: CVE-2015-3195
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2015-12-06
Source: https://osv.dev/vulnerability/CVE-2015-3195
Type: osv

## Details
The ASN1_TFLG_COMBINE implementation in crypto/asn1/tasn_dec.c in OpenSSL before 0.9.8zh, 1.0.0 before 1.0.0t, 1.0.1 before 1.0.1q, and 1.0.2 before 1.0.2e mishandles errors caused by malformed X509_ATTRIBUTE data, which allows remote attackers to obtain sensitive information from process memory by triggering a decoding failure in a PKCS#7 or CMS application.

## References
- http://fortiguard.com/advisory/openssl-advisory-december-2015
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10733
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10761
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00004.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/173801.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00017.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00070.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00071.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00087.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00103.html
- http://marc.info/?l=bugtraq&m=145382583417444&w=2
- http://openssl.org/news/secadv/20151203.txt
- http://rhn.redhat.com/errata/RHSA-2015-2616.html
- http://rhn.redhat.com/errata/RHSA-2015-2617.html
- http://rhn.redhat.com/errata/RHSA-2016-2056.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20151204-openssl
