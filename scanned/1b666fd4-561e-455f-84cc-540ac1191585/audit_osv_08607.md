# [M] CVE-2016-4796

## Summary
Severity: Medium
Advisory: CVE-2016-4796
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-4796
Type: osv

## Details
Heap-based buffer overflow in the color_cmyk_to_rgb in common/color.c in OpenJPEG before 2.1.1 allows remote attackers to cause a denial of service (crash) via a crafted .j2k file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FFMOZOF2EI6N2CR23EQ5EATWLQKBMHW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BJM23YERMEC6LCTWBUH7LZURGSLZDFDH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DFRD35RIPRCGZA5DKAKHZ62LMP2A5UT7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HPMDEUIMHTLKMHELDL4F4HZ7X4Y34JEB/
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.openwall.com/lists/oss-security/2016/05/13/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1335482
- https://github.com/uclouvain/openjpeg/commit/162f6199c0cd3ec1c6c6dc65e41b2faab92b2d91
- https://github.com/uclouvain/openjpeg/issues/774
