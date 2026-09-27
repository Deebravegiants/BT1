# [C] CVE-2016-0799

## Summary
Severity: Critical
Advisory: CVE-2016-0799
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-03-03
Source: https://osv.dev/vulnerability/CVE-2016-0799
Type: osv

## Details
The fmtstr function in crypto/bio/b_print.c in OpenSSL 1.0.1 before 1.0.1s and 1.0.2 before 1.0.2g improperly calculates string lengths, which allows remote attackers to cause a denial of service (overflow and out-of-bounds read) or possibly have unspecified other impact via a long string, as demonstrated by a large amount of ASN.1 data, a different vulnerability than CVE-2016-2842.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178358.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178817.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
- http://marc.info/?l=bugtraq&m=145983526810210&w=2
- http://marc.info/?l=bugtraq&m=146108058503441&w=2
