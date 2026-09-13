# [H] CVE-2021-3750

## Summary
Severity: High
Advisory: CVE-2021-3750
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2021-3750
Type: osv

## Details
A DMA reentrancy issue was found in the USB EHCI controller emulation of QEMU. EHCI does not verify if the Buffer Pointer overlaps with its MMIO region when it transfers the USB packets. Crafted content may be written to the controller's registers and trigger undesirable actions (such as reset) while the device is still transferring packets. This can ultimately lead to a use-after-free issue. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition, or potentially execute arbitrary code within the context of the QEMU process on the host. This flaw affects QEMU versions before 7.0.0.

## References
- https://gitlab.com/qemu-project/qemu/-/issues/556
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220624-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1999073
- https://gitlab.com/qemu-project/qemu/-/issues/541
