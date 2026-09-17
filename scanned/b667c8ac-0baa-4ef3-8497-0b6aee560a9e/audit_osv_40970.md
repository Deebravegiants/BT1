# [M] Craft CMS - Authenticated Path Traversal in assets/icon Extension Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-56394
Aliases: GHSA-c43v-4cr8-6mvp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56394
Type: osv

## Details
Craft CMS from 4.0.0-RC1 contains an authenticated path traversal vulnerability in the assets/icon endpoint where the extension parameter is not validated before file existence checks. Attackers can bypass extension validation by passing traversal sequences that resolve to existing SVG files, allowing local file read access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56394.json
- https://github.com/craftcms/cms/security/advisories/GHSA-c43v-4cr8-6mvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-56394
- https://www.vulncheck.com/advisories/craft-cms-authenticated-path-traversal-in-assets-icon-extension-parameter
- https://github.com/craftcms/cms/commit/30f5f1a8d6edf0f3a00be72c42c78d9dc7d72d5c
