# [M] CVE-2019-15034

## Summary
Severity: Medium
Advisory: CVE-2019-15034
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/CVE-2019-15034
Type: osv

## Details
hw/display/bochs-display.c in QEMU 4.0.0 does not ensure a sufficient PCI config space allocation, leading to a buffer overflow involving the PCIe extended config space.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00007.html
- https://usn.ubuntu.com/4372-1/
- https://www.debian.org/security/2020/dsa-4665
- https://lists.gnu.org/archive/html/qemu-devel/2019-08/msg01959.html
