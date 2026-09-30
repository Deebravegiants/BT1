# [H] fs/ntfs3: validate BOOT sectors_per_clusters

## Summary
Severity: High
Advisory: CVE-2022-49553
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49553
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.45, >=5.16.0 <5.17.13, >=5.18.0 <5.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: validate BOOT sectors_per_clusters

When the NTFS BOOT sectors_per_clusters field is > 0x80, it represents a
shift value.  Make sure that the shift value is not too large before using
it (NTFS max cluster size is 2MB).  Return -EVINVAL if it too large.

This prevents negative shift values and shift values that are larger than
the field size.

Prevents this UBSAN error:

 UBSAN: shift-out-of-bounds in ../fs/ntfs3/super.c:673:16
 shift exponent -192 is negative

## References
- https://git.kernel.org/stable/c/4746c49b11b2403f5b5b07c6eac9e60663dcd9a3
- https://git.kernel.org/stable/c/58cf68a1886d14ffdc5c892ce483a82156769e88
- https://git.kernel.org/stable/c/a2b6986316a2d106f6951e76db70fa4b2fde64a9
- https://git.kernel.org/stable/c/a3b774342fa752a5290c0de36375289dfcf4a260
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49553.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49553
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
