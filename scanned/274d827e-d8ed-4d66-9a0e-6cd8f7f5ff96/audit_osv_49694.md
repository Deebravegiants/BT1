# [M] CVE-2019-16233

## Summary
Severity: Medium
Advisory: CVE-2019-16233
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-16233
Type: osv

## Details
drivers/scsi/qla2xxx/qla_os.c in the Linux kernel 5.2.14 does not check the alloc_workqueue return value, leading to a NULL pointer dereference.

## References
- https://usn.ubuntu.com/4346-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00035.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- https://lkml.org/lkml/2019/9/9/487
