# [H] mm/mm_init: fix uninitialized struct pages for ZONE_DEVICE

## Summary
Severity: High
Advisory: CVE-2026-72172
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72172
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/mm_init: fix uninitialized struct pages for ZONE_DEVICE

If DAX memory is hotplugged into an unoccupied subsection of an early
section, section_activate() reuses the unoptimized boot memmap.  However,
compound_nr_pages() still assumes that vmemmap optimization is in effect
and initializes only the reduced number of struct pages.  As a result, the
remaining tail struct pages are left uninitialized, which can later lead
to unexpected behavior or crashes.

Fix this by treating early sections as unoptimized when calculating how
many struct pages to initialize.

## References
- https://git.kernel.org/stable/c/11f2826e9ee6f24aaa774e3dcd75abbe4b3091b6
- https://git.kernel.org/stable/c/511a60e71aec308b24722cffc1912bf6befb87bf
- https://git.kernel.org/stable/c/b91e27bce37cab9f35de0059278ebe457ca9878b
- https://git.kernel.org/stable/c/c5ef574d57e4a701485c13f26822328c91f05413
- https://git.kernel.org/stable/c/cd681403a87085562499d60325b7b45d3be11217
- https://git.kernel.org/stable/c/da5234df0941665f3a3f5b80f3dab94046537be0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
