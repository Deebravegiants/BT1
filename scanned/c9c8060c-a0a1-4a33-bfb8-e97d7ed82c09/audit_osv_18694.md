# [H] CVE-2020-35498

## Summary
Severity: High
Advisory: CVE-2020-35498
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-11
Source: https://osv.dev/vulnerability/CVE-2020-35498
Type: osv

## Details
A vulnerability was found in openvswitch. A limitation in the implementation of userspace packet parsing can allow a malicious user to send a specially crafted packet causing the resulting megaflow in the kernel to be too wide, potentially causing a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UJ4DXFJWMZ325ECZXPZOSK7BOEDJZHPR/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00032.html
- https://security.gentoo.org/glsa/202311-16
- https://www.debian.org/security/2021/dsa-4852
- https://bugzilla.redhat.com/show_bug.cgi?id=1908845
- https://www.openwall.com/lists/oss-security/2021/02/10/4
