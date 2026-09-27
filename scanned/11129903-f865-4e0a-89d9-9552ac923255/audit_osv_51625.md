# [M] CVE-2021-3630

## Summary
Severity: Medium
Advisory: CVE-2021-3630
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-30
Source: https://osv.dev/vulnerability/CVE-2021-3630
Type: osv

## Details
An out-of-bounds write vulnerability was found in DjVuLibre in DJVU::DjVuTXT::decode() in DjVuText.cpp via a crafted djvu file which may lead to crash and segmentation fault. This flaw affects DjVuLibre versions prior to 3.5.28.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MRXCW4BUGAJLGF6IWQWUZ2YBICMZCPK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CIZIAJWGKI26DKDOGJS7J7CIQGHHMIHG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q3B4QZCICPZRDXA2HOIACSQNZB2VEHSM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XVKYWV4P5XGA3FXKGFB443MKC32L7YQB/
- https://lists.debian.org/debian-lts-announce/2021/07/msg00002.html
- https://www.debian.org/security/2021/dsa-5032
- https://bugzilla.redhat.com/show_bug.cgi?id=1977427
