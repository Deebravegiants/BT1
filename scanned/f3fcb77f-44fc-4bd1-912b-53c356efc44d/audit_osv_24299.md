# [M] Qemu: lsi53c895a: dma reentrancy issue leads to stack overflow

## Summary
Severity: Medium
Advisory: CVE-2023-0330
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2023-0330
Type: osv

## Details
A vulnerability in the lsi53c895a device affects the latest version of qemu. A DMA-MMIO reentrancy problem may lead to memory corruption bugs like stack overflow or use-after-free.

## References
- https://lists.nongnu.org/archive/html/qemu-devel/2023-01/msg03411.html
- https://access.redhat.com/security/cve/CVE-2023-0330
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0330.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0330
- https://bugzilla.redhat.com/show_bug.cgi?id=2160151
- https://gitlab.com/qemu-project/qemu
- https://lists.debian.org/debian-lts-announce/2023/10/msg00006.html
