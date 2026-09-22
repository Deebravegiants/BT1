# [H] drm/amdkfd: Add bounds check for CRAT subtype length

## Summary
Severity: High
Advisory: CVE-2026-80747
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80747
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Add bounds check for CRAT subtype length

The CRAT parser validates that the subtype header fits within the image,
but does not verify that the advertised subtype length fits. A malformed
CRAT table with an oversized length field causes out-of-bounds reads when
kfd_parse_subtype() casts the header to specific subtype structures.

Add validation that sub_type_hdr + length does not exceed the image
boundary before parsing the subtype contents.

(cherry picked from commit 48e1d1e6e8798aef0312e68d8e586021b5b3cf4d)

## References
- https://git.kernel.org/stable/c/6e7566ba4739dd573c331adde1c96690f7a567bd
- https://git.kernel.org/stable/c/ca91e0cc8087568e4b791648a7c01e804f48cb73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80747.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
