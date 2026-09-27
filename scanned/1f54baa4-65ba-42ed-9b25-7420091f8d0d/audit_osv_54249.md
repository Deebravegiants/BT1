# [M] CVE-2023-4527

## Summary
Severity: Medium
Advisory: CVE-2023-4527
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-09-18
Source: https://osv.dev/vulnerability/CVE-2023-4527
Type: osv

## Details
A flaw was found in glibc. When the getaddrinfo function is called with the AF_UNSPEC address family and the system is configured with no-aaaa mode via /etc/resolv.conf, a DNS response via TCP larger than 2048 bytes can potentially disclose stack contents through the function returned address data, and may cause a crash.

## References
- https://access.redhat.com/errata/RHSA-2023:5453
- https://access.redhat.com/security/cve/CVE-2023-4527
- http://www.openwall.com/lists/oss-security/2023/09/25/1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DFG4P76UHHZEWQ26FWBXG76N2QLKKPZA/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NDAQWHTSVOCOZ5K6KPIWKRT3JX4RTZUR/
- https://security.gentoo.org/glsa/202310-03
- https://security.netapp.com/advisory/ntap-20231116-0012/
- https://access.redhat.com/errata/RHSA-2023:5455
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4DBUQRRPB47TC3NJOUIBVWUGFHBJAFDL/
- https://bugzilla.redhat.com/show_bug.cgi?id=2234712
