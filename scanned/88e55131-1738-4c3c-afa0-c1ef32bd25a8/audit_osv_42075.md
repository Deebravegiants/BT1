# [H] staging: rtl8723bs: fix OOB read in update_beacon_info() IE loop

## Summary
Severity: High
Advisory: CVE-2026-64443
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64443
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB read in update_beacon_info() IE loop

The IE parsing loop in update_beacon_info() advances by
(pIE->length + 2) each iteration but only guards on i < len.
When a malicious AP sends a Beacon whose last IE has only one byte
remaining in the frame (the element_id byte lands at len-1), the loop
reads pIE->length from one byte past the allocated receive buffer.

Additionally, even when the header bytes are in bounds, pIE->length
itself can extend the data window beyond len, passing a truncated IE
to the handler functions.

Add two guards at the top of the loop body:
  1. Break if fewer than sizeof(*pIE) bytes remain (can't read header).
  2. Break if the IE's declared data extends past len.

Also replace i += (pIE->length + 2) with i += sizeof(*pIE) + pIE->length
for consistency with the sizeof(*pIE) guards added above.

## References
- https://git.kernel.org/stable/c/5e8db4cff5b45c7c4edc8ae3f302027c3bb32b25
- https://git.kernel.org/stable/c/69f174a0673b6b7a29b851adb60bc450cdc0ecc4
- https://git.kernel.org/stable/c/6dd5e8c3011ebabf417257d7f07901a7c4311539
- https://git.kernel.org/stable/c/9193c34f75fd9e1ea8a590d7cced464c3380dc29
- https://git.kernel.org/stable/c/b5cc2f999927f69723ca53f1f2a3aa37dbeda907
- https://git.kernel.org/stable/c/bd953d52d587d42365e399b96c52dbdb13032070
- https://git.kernel.org/stable/c/ed51de4a86e173c3b0ef78e039c2e49e08b11f16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64443.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64443
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
