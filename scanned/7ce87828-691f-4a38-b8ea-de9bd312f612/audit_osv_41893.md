# [H] accel/qaic: Add overflow check to remap_pfn_range during mmap

## Summary
Severity: High
Advisory: CVE-2026-64051
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64051
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/qaic: Add overflow check to remap_pfn_range during mmap

The call to remap_pfn_range in qaic_gem_object_mmap is susceptible to
(re)mapping beyond the VMA if the BO is too large. This can cause use
after free issues when munmap() unmaps only the VMA region and not the
additional mappings. To prevent this, check the remaining size of the
VMA before remapping and truncate the remapped length if sg->length is
too large.

[jhugo: fix braces from checkpatch --strict]

## References
- https://git.kernel.org/stable/c/8c795012d0e06b7740e40319b86ff8d2a435098d
- https://git.kernel.org/stable/c/8dd6edbe26770df147136c3f2ac976c873b82650
- https://git.kernel.org/stable/c/97a8e89cdef36207a8776edc03d6931763a06ad0
- https://git.kernel.org/stable/c/9baafc2fea096279e75480f93fd5942e8336b510
- https://git.kernel.org/stable/c/aa16b2bc0f02709919e2435f531406531e5bcc69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64051.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
