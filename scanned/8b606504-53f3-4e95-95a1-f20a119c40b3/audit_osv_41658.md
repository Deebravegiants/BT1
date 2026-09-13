# [H] Copier: Percent-encoded dot segments in template URLs can allow trusted-prefix escape (Incomplete fix for trust-prefix bypass)

## Summary
Severity: High
Advisory: CVE-2026-62999
Aliases: GHSA-34mv-rjq9-5mch
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-62999
Type: osv

## Details
Copier is a library and CLI app for rendering project templates. From 9.5.0 through 9.16.0, percent-encoded parent-directory segments or encoded path separators in a template URL can match a configured trusted repository prefix before an HTTP server or Git transport decodes the path, allowing unsafe template features from a repository outside the trusted prefix to run after user interaction. This issue is fixed in version 9.17.0.

## References
- https://github.com/copier-org/copier/releases/tag/v9.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62999.json
- https://github.com/copier-org/copier/security/advisories/GHSA-34mv-rjq9-5mch
- https://nvd.nist.gov/vuln/detail/CVE-2026-62999
- https://github.com/copier-org/copier/commit/7408f0d6287a7bf452715fd9f25dc54eaba3c295
