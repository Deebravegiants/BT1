# [M] CVE-2021-3544

## Summary
Severity: Medium
Advisory: CVE-2021-3544
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3544
Type: osv

## Details
Several memory leaks were found in the virtio vhost-user GPU device (vhost-user-gpu) of QEMU in versions up to and including 6.0. They exist in contrib/vhost-user-gpu/vhost-user-gpu.c and contrib/vhost-user-gpu/virgl.c due to improper release of memory (i.e., free) after effective lifetime.

## References
- http://www.openwall.com/lists/oss-security/2021/05/31/1
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210720-0008/
- https://www.debian.org/security/2021/dsa-4980
- https://bugzilla.redhat.com/show_bug.cgi?id=1958935
