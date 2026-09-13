# [C] OpenProject is Vulnerable to Arbitrary File Read via ImageMagick SVG Coder

## Summary
Severity: Critical
Advisory: CVE-2026-22600
Aliases: GHSA-m8f2-cwpq-vvhh
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22600
Type: osv

## Details
OpenProject is an open-source, web-based project management software. A Local File Read (LFR) vulnerability exists in the work package PDF export functionality of OpenProject prior to version 16.6.4. By uploading a specially crafted SVG file (disguised as a PNG) as a work package attachment, an attacker can exploit the backend image processing engine (ImageMagick). When the work package is exported to PDF, the backend attempts to resize the image, triggering the ImageMagick text: coder. This allows an attacker to read arbitrary local files that the application user has permissions to access (e.g., /etc/passwd, all project configuration files, private project data, etc.). The attack requires permissions to upload attachments to a container that can be exported to PDF, such as a work package. The issue has been patched in version 16.6.4. Those who are unable to upgrade may apply the patch manually.

## References
- https://github.com/opf/openproject/releases/tag/v16.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22600.json
- https://github.com/opf/openproject/security/advisories/GHSA-m8f2-cwpq-vvhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-22600
