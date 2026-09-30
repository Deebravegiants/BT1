# [H] CVE-2019-19052

## Summary
Severity: High
Advisory: CVE-2019-19052
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19052
Type: osv

## Details
A memory leak in the gs_can_open() function in drivers/net/can/usb/gs_usb.c in the Linux kernel before 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering usb_submit_urb() failures, aka CID-fb5be6a7b486.

## References
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- https://usn.ubuntu.com/4228-1/
- https://usn.ubuntu.com/4228-2/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/torvalds/linux/commit/fb5be6a7b4863ecc44963bb80ca614584b6c7817
