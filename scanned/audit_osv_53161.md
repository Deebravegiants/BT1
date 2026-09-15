# [M] CVE-2022-3169

## Summary
Severity: Medium
Advisory: CVE-2022-3169
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2022-3169
Type: osv

## Details
A flaw was found in the Linux kernel. A denial of service flaw may occur if there is a consecutive request of the NVME_IOCTL_RESET and the NVME_IOCTL_SUBSYS_RESET through the device file of the driver, resulting in a PCIe link disconnect.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://bugzilla.kernel.org/show_bug.cgi?id=214771
