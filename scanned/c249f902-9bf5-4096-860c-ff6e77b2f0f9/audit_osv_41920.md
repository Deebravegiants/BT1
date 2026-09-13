# [H] drm/amd/display: Validate GPIO pin LUT table size before iterating

## Summary
Severity: High
Advisory: CVE-2026-64097
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64097
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Validate GPIO pin LUT table size before iterating

[Why&How]
The GPIO pin table parsers in get_gpio_i2c_info() and
bios_parser_get_gpio_pin_info() derive an element count from the VBIOS
table_header.structuresize field, then iterate over gpio_pin[] entries.
However, GET_IMAGE() only validates that the table header itself fits
within the BIOS image. If the VBIOS reports a structuresize larger than
the actual mapped data, the loop reads past the end of the BIOS image,
causing an out-of-bounds read.

Fix this by calling bios_get_image() to validate that the full claimed
structuresize is accessible within the BIOS image before entering the
loop in both functions.

(cherry picked from commit ba5e95b43b773ae1bf1f66ee6b31eb774e65afe3)

## References
- https://git.kernel.org/stable/c/67461e0c15335894cc5d3b84cda823bf8cbdc886
- https://git.kernel.org/stable/c/7ca695b3122297b06a3ed605bbe1cd32c85d9f5a
- https://git.kernel.org/stable/c/86d2b20644b11d21fe52c596e6e922b4590a3e3f
- https://git.kernel.org/stable/c/9900f6954be779011e7c2cd42addd87baf028bc5
- https://git.kernel.org/stable/c/f2a4827e980ba07de4391fa84d9c39a12726bdd7
- https://git.kernel.org/stable/c/fb30a3890d62fd50a95aef684faf64a307592e42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64097.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
