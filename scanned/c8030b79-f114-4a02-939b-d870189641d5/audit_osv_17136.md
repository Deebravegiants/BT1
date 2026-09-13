# [C] CVE-2020-12823

## Summary
Severity: Critical
Advisory: CVE-2020-12823
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-12823
Type: osv

## Details
OpenConnect 8.09 has a buffer overflow, causing a denial of service (application crash) or possibly unspecified other impact, via crafted certificate data to get_cert_name in gnutls.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/25MFX4AZE7RDCUWOL4ZOE73YBOPUMQDX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AYSXLXAPXD2T73T6JMHI5G2WP7KHAGMN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEVTIH5UFX35CC7MVSYBGRM3D66ACFD5/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00056.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00015.html
- https://security.gentoo.org/glsa/202006-15
- https://gitlab.com/openconnect/openconnect/-/merge_requests/108
- https://bugs.gentoo.org/721570
