# [M] InvenTree has Path Traversal In Report Templates

## Summary
Severity: Medium
Advisory: CVE-2026-33531
Aliases: GHSA-rhc5-7c3r-c769
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33531
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. Prior to version 1.2.6, a path traversal vulnerability in the report template engine allows a staff-level user to read arbitrary files from the server filesystem via crafted template tags. Affected functions: `encode_svg_image()`, `asset()`, and `uploaded_image()` in `src/backend/InvenTree/report/templatetags/report.py`. This requires staff access (to upload / edit templates with maliciously crafted tags). If the InvenTree installation is configured with high access privileges on the host system, this path traversal may allow file access outside of the InvenTree source directory. This issue is patched in version 1.2.6, and 1.3.0 (or above). Users should update to the patched versions. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33531.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-rhc5-7c3r-c769
- https://nvd.nist.gov/vuln/detail/CVE-2026-33531
- https://github.com/inventree/InvenTree/pull/11579
