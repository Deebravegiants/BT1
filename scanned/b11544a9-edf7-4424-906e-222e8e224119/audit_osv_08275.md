# [M] CVE-2016-2107

## Summary
Severity: Medium
Advisory: CVE-2016-2107
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2107
Type: osv

## Details
The AES-NI implementation in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h does not consider memory allocation during a certain padding check, which allows remote attackers to obtain sensitive cleartext information via a padding-oracle attack against an AES CBC session. NOTE: this vulnerability exists because of an incorrect fix for CVE-2013-0169.

## References
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=68595c0c2886e7942a14f98c17a55a88afb6c292
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183457.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183607.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184605.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00019.html
- http://packetstormsecurity.com/files/136912/Slackware-Security-Advisory-openssl-Updates.html
- http://rhn.redhat.com/errata/RHSA-2016-0722.html
- http://rhn.redhat.com/errata/RHSA-2016-0996.html
- http://rhn.redhat.com/errata/RHSA-2016-2073.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://source.android.com/security/bulletin/2016-07-01.html
