# [M] CVE-2023-5158

## Summary
Severity: Medium
Advisory: CVE-2023-5158
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-25
Source: https://osv.dev/vulnerability/CVE-2023-5158
Type: osv

## Details
A flaw was found in vringh_kiov_advance in drivers/vhost/vringh.c in the host side of a virtio ring in the Linux Kernel. This issue may result in a denial of service from guest to host via zero length descriptor.

## References
- https://access.redhat.com/security/cve/CVE-2023-5158
- https://bugzilla.redhat.com/show_bug.cgi?id=2240561
