# [H] CVE-2015-8472

## Summary
Severity: High
Advisory: CVE-2015-8472
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-01-21
Source: https://osv.dev/vulnerability/CVE-2015-8472
Type: osv

## Details
Buffer overflow in the png_set_PLTE function in libpng before 1.0.65, 1.1.x and 1.2.x before 1.2.55, 1.3.x, 1.4.x before 1.4.18, 1.5.x before 1.5.25, and 1.6.x before 1.6.20 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a small bit-depth value in an IHDR (aka image header) chunk in a PNG image.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-8126.

## References
- http://rhn.redhat.com/errata/RHSA-2015-2594.html
- http://rhn.redhat.com/errata/RHSA-2015-2595.html
- http://rhn.redhat.com/errata/RHSA-2015-2596.html
- http://rhn.redhat.com/errata/RHSA-2016-0055.html
- http://rhn.redhat.com/errata/RHSA-2016-0056.html
- http://rhn.redhat.com/errata/RHSA-2016-0057.html
- http://www.debian.org/security/2016/dsa-3443
- http://www.oracle.com/technetwork/topics/security/cpujan2016-2367955.html
- https://access.redhat.com/errata/RHSA-2016:1430
- https://support.apple.com/HT206167
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00004.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174905.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174936.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175073.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00043.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00045.html
