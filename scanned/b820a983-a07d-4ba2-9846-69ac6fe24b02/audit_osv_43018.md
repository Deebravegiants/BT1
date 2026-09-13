# [H] accel/amdxdna: Fix VMA access race

## Summary
Severity: High
Advisory: CVE-2026-72331
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72331
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Fix VMA access race

aie2_populate_range() and amdxdna_umap_release() access a saved VMA
pointer that may have already been freed, leading to a potential
use-after-free.

Remove the VMA accesses from these functions to avoid the race.

## References
- https://git.kernel.org/stable/c/1ba02717e821cf14ece642273958647e79698d3d
- https://git.kernel.org/stable/c/bea20225c67fed9be3e98619c77af6ee3f43fe07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72331.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72331
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
