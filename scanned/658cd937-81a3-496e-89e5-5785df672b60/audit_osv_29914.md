# [H] scsi: sd: Fix off-by-one error in sd_read_block_characteristics()

## Summary
Severity: High
Advisory: CVE-2024-47682
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47682
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: sd: Fix off-by-one error in sd_read_block_characteristics()

Ff the device returns page 0xb1 with length 8 (happens with qemu v2.x, for
example), sd_read_block_characteristics() may attempt an out-of-bounds
memory access when accessing the zoned field at offset 8.

## References
- https://git.kernel.org/stable/c/413df704f149dec585df07466d2401bbd1f490a0
- https://git.kernel.org/stable/c/568c7c4c77eee6df7677bb861b7cee7398a3255d
- https://git.kernel.org/stable/c/60312ae7392f9c75c6591a52fc359cf7f810d48f
- https://git.kernel.org/stable/c/a776050373893e4c847a49abeae2ccb581153df0
- https://git.kernel.org/stable/c/f81eaf08385ddd474a2f41595a7757502870c0eb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47682.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
