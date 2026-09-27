# [H] CVE-2015-3194

## Summary
Severity: High
Advisory: CVE-2015-3194
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-12-06
Source: https://osv.dev/vulnerability/CVE-2015-3194
Type: osv

## Details
crypto/rsa/rsa_ameth.c in OpenSSL 1.0.1 before 1.0.1q and 1.0.2 before 1.0.2e allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via an RSA PSS ASN.1 signature that lacks a mask generation function parameter.

## References
- http://fortiguard.com/advisory/openssl-advisory-december-2015
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10761
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/173801.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00053.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00070.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00071.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00087.html
- http://marc.info/?l=bugtraq&m=145382583417444&w=2
- http://openssl.org/news/secadv/20151203.txt
- http://rhn.redhat.com/errata/RHSA-2015-2617.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20151204-openssl
- http://www.debian.org/security/2015/dsa-3413
- http://www.fortiguard.com/advisory/openssl-advisory-december-2015
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
