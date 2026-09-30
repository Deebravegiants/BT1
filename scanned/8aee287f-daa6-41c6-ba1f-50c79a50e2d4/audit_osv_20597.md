# [M] CVE-2021-3545

## Summary
Severity: Medium
Advisory: CVE-2021-3545
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3545
Type: osv

## Details
An information disclosure vulnerability was found in the virtio vhost-user GPU device (vhost-user-gpu) of QEMU in versions up to and including 6.0. The flaw exists in virgl_cmd_get_capset_info() in contrib/vhost-user-gpu/virgl.c and could occur due to the read of uninitialized memory. A malicious guest could exploit this issue to leak memory from the host.

## References
- http://www.openwall.com/lists/oss-security/2021/05/31/1
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210720-0008/
- https://www.debian.org/security/2021/dsa-4980
- https://bugzilla.redhat.com/show_bug.cgi?id=1958955
