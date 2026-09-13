# [M] efi: runtime: Fix potential overflow of soft-reserved region size

## Summary
Severity: Medium
Advisory: CVE-2024-26843
Ecosystem: Linux
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26843
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi: runtime: Fix potential overflow of soft-reserved region size

md_size will have been narrowed if we have >= 4GB worth of pages in a
soft-reserved region.

## References
- https://git.kernel.org/stable/c/156cb12ffdcf33883304f0db645e1eadae712fe0
- https://git.kernel.org/stable/c/4aa36b62c3eaa869860bf78b1146e9f2b5f782a9
- https://git.kernel.org/stable/c/4fff3d735baea104017f2e3c245e27cdc79f2426
- https://git.kernel.org/stable/c/700c3f642c32721f246e09d3a9511acf40ae42be
- https://git.kernel.org/stable/c/cf3d6813601fe496de7f023435e31bfffa74ae70
- https://git.kernel.org/stable/c/de1034b38a346ef6be25fe8792f5d1e0684d5ff4
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26843.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26843
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
