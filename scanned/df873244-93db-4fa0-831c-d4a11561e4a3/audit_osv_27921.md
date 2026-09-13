# [H] riscv: Sparse-Memory/vmemmap out-of-bounds fix

## Summary
Severity: High
Advisory: CVE-2024-26795
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26795
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: Sparse-Memory/vmemmap out-of-bounds fix

Offset vmemmap so that the first page of vmemmap will be mapped
to the first page of physical memory in order to ensure that
vmemmap’s bounds will be respected during
pfn_to_page()/page_to_pfn() operations.
The conversion macros will produce correct SV39/48/57 addresses
for every possible/valid DRAM_BASE inside the physical memory limits.

v2:Address Alex's comments

## References
- https://git.kernel.org/stable/c/2a1728c15ec4f45ed9248ae22f626541c179bfbe
- https://git.kernel.org/stable/c/5941a90c55d3bfba732b32208d58d997600b44ef
- https://git.kernel.org/stable/c/8310080799b40fd9f2a8b808c657269678c149af
- https://git.kernel.org/stable/c/8af1c121b0102041809bc137ec600d1865eaeedd
- https://git.kernel.org/stable/c/a11dd49dcb9376776193e15641f84fcc1e5980c9
- https://git.kernel.org/stable/c/a278d5c60f21aa15d540abb2f2da6e6d795c3e6e
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26795.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26795
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
