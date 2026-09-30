# [M] CVE-2025-46206

## Summary
Severity: Medium
Advisory: CVE-2025-46206
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-08-04
Source: https://osv.dev/vulnerability/CVE-2025-46206
Type: osv

## Details
An issue in Artifex mupdf 1.25.6, 1.25.5 allows a remote attacker to cause a denial of service via an infinite recursion in the `mutool clean` utility. When processing a crafted PDF file containing cyclic /Next references in the outline structure, the `strip_outline()` function enters infinite recursion

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708521
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=0ec7e4d2201bb6df217e01c17396d36297abf9ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46206.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46206
- https://github.com/Landw-hub/CVE-2025-46206
