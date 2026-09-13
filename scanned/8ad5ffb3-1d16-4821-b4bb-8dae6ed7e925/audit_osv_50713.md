# [M] CVE-2020-29570

## Summary
Severity: Medium
Advisory: CVE-2020-29570
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29570
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. Recording of the per-vCPU control block mapping maintained by Xen and that of pointers into the control block is reversed. The consumer assumes, seeing the former initialized, that the latter are also ready for use. Malicious or buggy guest kernels can mount a Denial of Service (DoS) attack affecting the entire system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2C6M6S3CIMEBACH6O7V4H2VDANMO6TVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OBLV6L6Q24PPQ2CRFXDX4Q76KU776GKI/
- http://www.openwall.com/lists/oss-security/2020/12/16/4
- https://security.gentoo.org/glsa/202107-30
- https://www.debian.org/security/2020/dsa-4812
- https://xenbits.xenproject.org/xsa/advisory-358.html
