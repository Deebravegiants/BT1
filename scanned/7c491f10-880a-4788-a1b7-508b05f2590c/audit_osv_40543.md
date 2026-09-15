# [M] ImageMagick: Use-After-Free when allocation in CheckPrimitiveExtent fails

## Summary
Severity: Medium
Advisory: CVE-2026-53462
Aliases: GHSA-px7q-ggqj-hcf2
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53462
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-50 and 7.1.2-25, when an allocation fails in CheckPrimitiveExtent this can result in a heap-use-after-free and result in a crash. This issue has been patched in versions 6.9.13-50 and 7.1.2-25.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53462.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-px7q-ggqj-hcf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-53462
