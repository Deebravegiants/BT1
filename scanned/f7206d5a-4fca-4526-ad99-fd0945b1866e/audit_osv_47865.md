# [M] CVE-2017-14051

## Summary
Severity: Medium
Advisory: CVE-2017-14051
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14051
Type: osv

## Details
An integer overflow in the qla2x00_sysfs_write_optrom_ctl function in drivers/scsi/qla2xxx/qla_attr.c in the Linux kernel through 4.12.10 allows local users to cause a denial of service (memory corruption and system crash) by leveraging root access.

## References
- http://www.securityfocus.com/bid/100571
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://bugzilla.kernel.org/show_bug.cgi?id=194061
- https://patchwork.kernel.org/patch/9929625/
