# [M] CVE-2017-17558

## Summary
Severity: Medium
Advisory: CVE-2017-17558
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-17558
Type: osv

## Details
The usb_destroy_configuration function in drivers/usb/core/config.c in the USB core subsystem in the Linux kernel through 4.14.5 does not consider the maximum number of configurations and interfaces before attempting to release resources, which allows local users to cause a denial of service (out-of-bounds write access) or possibly have unspecified other impact via a crafted USB device.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00004.html
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3754-1/
- https://www.debian.org/security/2017/dsa-4073
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://openwall.com/lists/oss-security/2017/12/12/7
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2019:1170
- https://www.debian.org/security/2018/dsa-4082
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2019:1190
- https://www.spinics.net/lists/linux-usb/msg163644.html
