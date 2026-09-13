# [M] CVE-2023-23004

## Summary
Severity: Medium
Advisory: CVE-2023-23004
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-23004
Type: osv

## Details
In the Linux kernel before 5.19, drivers/gpu/drm/arm/malidp_planes.c misinterprets the get_sg_table return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23004.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23004
- https://github.com/torvalds/linux/commit/15342f930ebebcfe36f2415049736a77d7d2e045
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
