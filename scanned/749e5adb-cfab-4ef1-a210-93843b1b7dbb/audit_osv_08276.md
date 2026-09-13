# [C] CVE-2016-2108

## Summary
Severity: Critical
Advisory: CVE-2016-2108
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2108
Type: osv

## Details
The ASN.1 implementation in OpenSSL before 1.0.1o and 1.0.2 before 1.0.2c allows remote attackers to execute arbitrary code or cause a denial of service (buffer underflow and memory corruption) via an ANY field in crafted serialized data, aka the "negative zero" issue.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183457.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183607.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184605.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00055.html
