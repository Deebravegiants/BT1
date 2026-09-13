# [M] CVE-2026-86142

## Summary
Severity: Medium
Advisory: CVE-2026-86142
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86142
Type: osv

## Details
In libxml2 before 2.15.4, there is a heap-based buffer overflow in xmlXPtrEvalXPtrPart because of xmlXPtrEval xpointer length saturation.

## References
- https://github.com/GNOME/libxml2/compare/v2.15.3...v2.15.4
- https://gitlab.gnome.org/GNOME/libxml2/-/work_items/1113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86142.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86142
- https://github.com/GNOME/libxml2/commit/6b3a736c0edc74ceec3d82f5252499d7911b3a58
