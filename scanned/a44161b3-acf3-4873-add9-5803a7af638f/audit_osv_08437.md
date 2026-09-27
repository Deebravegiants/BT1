# [M] CVE-2016-3183

## Summary
Severity: Medium
Advisory: CVE-2016-3183
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-3183
Type: osv

## Details
The sycc422_t_rgb function in common/color.c in OpenJPEG before 2.1.1 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted jpeg2000 file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5FFMOZOF2EI6N2CR23EQ5EATWLQKBMHW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BJM23YERMEC6LCTWBUH7LZURGSLZDFDH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DFRD35RIPRCGZA5DKAKHZ62LMP2A5UT7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HPMDEUIMHTLKMHELDL4F4HZ7X4Y34JEB/
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.openwall.com/lists/oss-security/2016/03/16/17
- https://bugzilla.redhat.com/show_bug.cgi?id=1317821
- https://github.com/uclouvain/openjpeg/commit/15f081c89650dccee4aa4ae66f614c3fdb268767
- https://github.com/uclouvain/openjpeg/issues/726
- https://security.gentoo.org/glsa/201612-26
