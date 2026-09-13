# [H] CVE-2021-3546

## Summary
Severity: High
Advisory: CVE-2021-3546
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3546
Type: osv

## Details
An out-of-bounds write vulnerability was found in the virtio vhost-user GPU device (vhost-user-gpu) of QEMU in versions up to and including 6.0. The flaw occurs while processing the 'VIRTIO_GPU_CMD_GET_CAPSET' command from the guest. It could allow a privileged guest user to crash the QEMU process on the host, resulting in a denial of service condition, or potential code execution with the privileges of the QEMU process.

## References
- http://www.openwall.com/lists/oss-security/2021/05/31/1
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20210720-0008/
- https://www.debian.org/security/2021/dsa-4980
- https://bugzilla.redhat.com/show_bug.cgi?id=1958978
