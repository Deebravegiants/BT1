# [H] CVE-2021-47475

## Summary
Severity: High
Advisory: CVE-2021-47475
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47475
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: vmk80xx: fix transfer-buffer overflows

The driver uses endpoint-sized USB transfer buffers but up until
recently had no sanity checks on the sizes.

Commit e1f13c879a7c ("staging: comedi: check validity of wMaxPacketSize
of usb endpoints found") inadvertently fixed NULL-pointer dereferences
when accessing the transfer buffers in case a malicious device has a
zero wMaxPacketSize.

Make sure to allocate buffers large enough to handle also the other
accesses that are done without a size check (e.g. byte 18 in
vmk80xx_cnt_insn_read() for the VMK8061_MODEL) to avoid writing beyond
the buffers, for example, when doing descriptor fuzzing.

The original driver was for a low-speed device with 8-byte buffers.
Support was later added for a device that uses bulk transfers and is
presumably a full-speed device with a maximum 64-byte wMaxPacketSize.

## References
- https://git.kernel.org/stable/c/ec85bcff4ed09260243d8f39faba99e1041718ba
- https://git.kernel.org/stable/c/06ac746d57e6d32b062e220415c607b7e2e0fa50
- https://git.kernel.org/stable/c/199acd8c110e3ae62833c24f632b0bb1c9f012a9
- https://git.kernel.org/stable/c/7a2021b896de1ad559d33b5c5cdd20b982242088
- https://git.kernel.org/stable/c/a23461c47482fc232ffc9b819539d1f837adf2b1
- https://git.kernel.org/stable/c/278484ae93297b1bb1ce755f9d3b6d95a48c7d47
- https://git.kernel.org/stable/c/33d7a470730dfe7c9bfc8da84575cf2cedd60d00
- https://git.kernel.org/stable/c/40d2a7e278e2e7c0a5fd7e997e7eb63945bf93f7
- https://git.kernel.org/stable/c/5229159f1d052821007aff1a1beb7873eacf1a9f
