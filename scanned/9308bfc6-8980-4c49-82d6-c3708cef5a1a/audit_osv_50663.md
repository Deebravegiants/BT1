# [M] CVE-2020-27661

## Summary
Severity: Medium
Advisory: CVE-2020-27661
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-27661
Type: osv

## Details
A divide-by-zero issue was found in dwc2_handle_packet in hw/usb/hcd-dwc2.c in the hcd-dwc2 USB host controller emulation of QEMU. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=bea2a9e3e00b275dc40cfa09c760c715b8753e03
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1770368.html
- https://security.netapp.com/advisory/ntap-20210720-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=1890653
- https://lists.nongnu.org/archive/html/qemu-devel/2020-10/msg04263.html
