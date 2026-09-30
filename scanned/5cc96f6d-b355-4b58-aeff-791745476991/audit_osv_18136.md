# [M] CVE-2020-24352

## Summary
Severity: Medium
Advisory: CVE-2020-24352
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-24352
Type: osv

## Details
An issue was discovered in QEMU through 5.1.0. An out-of-bounds memory access was found in the ATI VGA device implementation. This flaw occurs in the ati_2d_blt() routine in hw/display/ati_2d.c while handling MMIO write operations through the ati_mm_write() callback. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service.

## References
- https://git.qemu.org/?p=qemu.git
- https://security.netapp.com/advisory/ntap-20201123-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1847584
